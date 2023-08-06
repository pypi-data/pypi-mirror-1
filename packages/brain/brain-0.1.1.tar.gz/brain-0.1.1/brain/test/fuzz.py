"""Database fuzz testing"""

import random
import string
import copy
import traceback
import time

import brain
from brain.connection import FakeConnection

STARTING_DEPTH = 5 # starting data depth of objects
MAX_DEPTH = 5 # maximum depth of data structures created during test
MAX_ELEMENTS_NUM = 3 # maximum number of elements in created lists/dictionaries
STOP_DATA_GENERATION = 0.6 # probability of stopping data generation on each level of structure
STOP_PATH_GENERATION = 0.1 # probability of stopping path generation on each level of structure
NONE_PROBABILITY = 0.3 # probability of last None appearance in the path of insert request

# Auxiliary functions

def getRandomString():
	return "".join(random.sample(string.ascii_letters + string.digits, 8))

def getRandomValue():
	funcs = [
		lambda: None,
		lambda: random.randint(-100, 100),
		lambda: random.random() * 200 - 100,
		lambda: getRandomString(),
		lambda: bytes(getRandomString(), 'ascii')
	]

	return random.choice(funcs)()

def getRandomData(depth):
	if depth == 0 or random.random() < STOP_DATA_GENERATION:
		return getRandomValue()

	length = random.randint(1, MAX_ELEMENTS_NUM)
	if random.choice([False, True]):
		return [getRandomData(depth - 1) for x in range(length)]
	else:
		return {getRandomString(): getRandomData(depth - 1) for x in range(length)}

def getRandomNonTrivialData(depth):
	"""Returns non-None random data structure"""
	data = None
	while not isinstance(data, list) and not isinstance(data, dict):
		data = getRandomData(depth)
	return data

def getRandomPath(root):
	"""Returns path to random element of given structure"""
	if random.random() < STOP_PATH_GENERATION:
		return []

	if isinstance(root, list):
		if len(root) == 0:
			return [None]
		else:
			random_index = random.randrange(len(root))
			return [random_index] + getRandomPath(root[random_index])
	elif isinstance(root, dict) and len(root) > 0:
		random_key = random.choice(list(root.keys()))
		return [random_key] + getRandomPath(root[random_key])
	else:
		return []

def getRandomDefinitePath(root):
	"""Returns random path without Nones"""
	path = [None]
	while None in path:
		path = getRandomPath(root)
	return path

def getRandomDeletePath(root):
	"""
	Returns random path for delete request -
	definite non-zero path, because mask deletion is hard to support in fuzz test,
	and we want to avoid deletion of the object
	"""
	path = []
	while len(path) == 0:
		path = getRandomDefinitePath(root)
	return path

def getRandomInsertPath(root):
	"""
	Returns random path for the target of insert request -
	random path, pointing to list, probably with the None in the end
	Warning: the function will last forever if there is not any list in data
	"""
	path = []
	while len(path) == 0 or isinstance(path[-1], str):
		path = getRandomPath(root)
	if random.random() < NONE_PROBABILITY:
		path[-1] = None
	return path

def listInData(data):
	"""Returns True if there is a list in given data structure"""
	if isinstance(data, list):
		return True
	elif isinstance(data, dict):
		for key in data:
			if listInData(data[key]): return True
		return False
	else:
		return False


class RandomAction:
	"""Class, representing an action on a given object"""

	def __init__(self, obj_contents):
		self._obj_contents = obj_contents

		args_constructors = {
			'modify': self._constructModifyArgs,
			'insertMany': self._constructInsertArgs,
			'deleteMany': self._constructDeleteArgs
		}

		if type(self._obj_contents) not in [list, dict] or len(self._obj_contents) == 0:
			del args_constructors['deleteMany']
		if not listInData(self._obj_contents):
			del args_constructors['insertMany']

		self._args = ()
		self._kwds = {}
		self._method = random.choice(list(args_constructors.keys()))
		args_constructors[self._method]()

	def dump(self, verbosity):
		return (str(self) if verbosity > 3 else self._method)

	def _constructModifyArgs(self):
		self._args = (getRandomDefinitePath(self._obj_contents),
			getRandomData(MAX_DEPTH))

	def _constructInsertArgs(self):
		elems = random.randint(1, MAX_ELEMENTS_NUM)
		to_insert = [getRandomData(MAX_DEPTH) for i in range(elems)]
		self._args = (getRandomInsertPath(self._obj_contents), to_insert)

	def _constructDeleteArgs(self):
		self._args = ([getRandomDeletePath(self._obj_contents)],)

	def __call__(self, conn, obj_id):
		args = self._args
		kwds = self._kwds
		getattr(conn, self._method)(obj_id, *args, **kwds)

	def __str__(self):
		return self._method + repr(self._args)


def _runTests(objects, actions, verbosity):
	"""Main test function. Create several objects and perform random actions on them."""

	# using default engine, because we are testing only DB logic here
	engine_tag = brain.getDefaultEngineTag()

	# create brain connection and fake Python-powered connection
	conn = brain.connect(None, name=None)
	fake_conn = FakeConnection()

	objs = []
	fake_objs = []

	# create objects
	for i in range(objects):
		data = getRandomNonTrivialData(STARTING_DEPTH)

		try:
			objs.append(conn.create(data))
		except:
			print("Error creating object: " + str(data))
			raise

		if verbosity > 2:
			print("Object " + str(i) + " created" +
				(", initial state: " + repr(data) if verbosity > 3 else ""))

		fake_objs.append(fake_conn.create(data))

	# perform test
	for c in range(actions):
		for i in range(objects):

			# copy original state in case we delete object or some error occurs
			fake_state_before = copy.deepcopy(fake_conn.read(fake_objs[i]))

			# try to read the real object from the database
			try:
				state_before = conn.read(objs[i])
			except:
				print("Error reading object " + str(i) +
					(": " + str(fake_state_before) if verbosity > 3 else ""))
				if verbosity > 3:
					conn._engine.dump()
				raise

			# create random action and test it on fake object
			action = RandomAction(state_before)
			action(fake_conn, fake_objs[i])

			# if object gets deleted, return its state to original
			fake_state_after = fake_conn.read(fake_objs[i])
			if fake_state_after is None:
				fake_conn.modify(fake_objs[i], fake_state_before, [])
				continue

			# try to perform action on a real object
			try:
				action(conn, objs[i])
			except:
				print("Error performing action on object " + str(i) +
					": " + action.dump())
				if verbosity > 3:
					print("State before: " + str(fake_state_before))
					conn._engine.dump()
				raise

			if verbosity > 2:
				print("Object " + str(i) + ", " + action.dump(verbosity))

			# try to read resulting object state
			try:
				state_after = conn.read(objs[i])
			except:
				print("Error reading object " + str(i) +
					((": " + str(fake_state_after)) if verbosity > 3 else ""))
				print("After action: " + action.dump(verbosity))
				if verbosity > 3:
					print("On state: " + str(fake_state_before))
					conn._engine.dump()
				raise

			# compare resulting states of real and fake objects
			if state_after != fake_state_after:
				print("Action results are different:")
				print("State before: " + repr(fake_state_before))
				print("Action: " + action.dump(verbosity))
				print("Main state after: " + repr(state_after))
				print("Fake state after: " + repr(fake_state_after))
				if verbosity > 3:
					conn._engine.dump()
				raise Exception("Functionality error")


def runFuzzTest(objects=1, actions=100, verbosity=2, seed=0):
	"""Main test function. Start test, terminate on first exception"""

	print("Fuzz test")

	if seed != 0:
		random.seed(seed)
		state = "seed: " + str(seed)
	else:
		random.seed()
		state = "random seed"

	print(str(objects) + " objects, " + str(actions) + " actions, " + state)

	print("=" * 70)
	time1 = time.time()
	try:
		_runTests(objects, actions, verbosity)
	except:
		err_class, err_obj, err_tb = err
		self.__stream.writeln("! " + str(err_obj))

		# report traceback
		if verbosity > 1:
			traceback.print_tb(err_tb, None, self.__stream)
	finally:
		print("=" * 70)
		time2 = time.time()
		print("Finished in {0:.3f} seconds".format(time2 - time1))
