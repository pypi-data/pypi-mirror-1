#
# MACHINA
# pdp
# GNUCITIZEN (http://www.gnucitizen.org)
#
__version__ = '0.1'

#
# STANDARD IMPORTS
#
import logging

#
# TASK EXCEPTIONS
#
class TaskException(Exception): pass
class TaskNameAlreadyUsed(TaskException): pass
class TaskAlreadyRegistered(TaskException): pass
class UnresolvedTaskDependenciesFound(TaskException): pass

#
# TASK
#
class task(object):
	__triggers__ = []
	__registered_tasks__ = {}
	__task_execution_chain__ = []

	def __init__(self, *args, **kwargs):
		defaults = {'name':None, 'description':None, 'dependencies':[], 'retries':None, 'timeout':None}

		for key, value in defaults.items():
			setattr(self, key, value)

		if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
			# variant 1: no arguments passed to the decorator
			self.name = args[0].__name__
			self.description = args[0].__doc__
			self.__func__ = args[0]
			self.__variant__ = 1

			task.register_task(self)
		else:
			# variant 2: some arguments passed to the decorator
			try:
				keys = defaults.keys()
				for i in range(0, len(args)):
					setattr(self, keys[i], args[i])
			except:
				pass

			for key, value in kwargs.items():
				setattr(self, key, value)

			self.__variant__ = 2

		if self.retries < 1:
			self.retries = None

		if self.timeout < 1:
			self.timeout = None

	def __call__(self, *args, **kwargs):
		if self.__variant__ == 1:
			return self.call(*args, **kwargs)
		else:
			if self.name is None:
				self.name = args[0].__name__

			if self.description is None:
				self.description = args[0].__doc__

			self.__func__ = args[0]
			self.__variant__ = 1

			task.register_task(self)

			return self

	def call(self, *args, **kwargs):
		return self.__func__(*args, **kwargs)

	@staticmethod
	def register_task(t):
		if task.__registered_tasks__.has_key(t.name):
			if task.__registered_tasks__[t.name] == t:
				raise TaskNameAlreadyUsed('task name already used')
			else:
				raise TaskAlreadyRegistered('task already registered')
		else:
			task.__registered_tasks__[t.name] = t

		if t.dependencies:
			dependencies = filter(lambda i: not (type(i) is task or task.__registered_tasks__.has_key(i)), t.dependencies)

			if dependencies:
				def trigger():
					for d in dependencies:
						if not task.__registered_tasks__.has_key(d):
							return False

					task.__task_execution_chain__.append(t)

					return True

				trigger.task = t

				task.__triggers__.append(trigger)

				return False
			else:
				task.__task_execution_chain__.append(t)
		else:
			task.__task_execution_chain__.append(t)

		task.__triggers__ = filter(lambda t: not t(), task.__triggers__)

		return True

	@staticmethod
	def call_task(t, *args, **kwargs):
		message = t(*args, **kwargs)

		if message:
			if type(message) is str:
				yield message
			else:
				try:
					it = iter(message)
				except:
					yield repr(message)
				else:
					for i in it:
						yield i

	@staticmethod
	def call_tasks(*args, **kwargs):
		if task.__triggers__:
			raise UnresolvedTaskDependenciesFound('unresolved task dependencies found for tasks %s' % ', '.join([t.task.name for t in task.__triggers__]))

		for t in task.__task_execution_chain__:
			yield t

			for m in task.call_task(t, *args, **kwargs):
				yield m

	@staticmethod
	def launch_task(t, *args, **kwargs):
		logging.info('launching task %s...' % t.name)

		try:
			for m in task.call_task(t, *args, **kwargs):
				logging.log(LogFormatter.MESSAGE, str(m))
		except Exception, e:
			logging.exception(e)

	@staticmethod
	def launch_tasks(*args, **kwargs):
		if task.__triggers__:
			raise UnresolvedTaskDependenciesFound('unresolved task dependencies found for tasks %s' % ', '.join([t.task.name for t in task.__triggers__]))

		for t in task.__task_execution_chain__:
			task.launch_task(t, *args, **kwargs)

#
# LOG FORMATTER
#
class LogFormatter(logging.Formatter):
	MESSAGE = 12321
	format_string = '[+] %(levelname)s|%(module)s|%(asctime)s|%(message)s'

	def __init__(self, fmt=None, datefmt=None):
		if fmt is None:
			fmt = self.format_string

		return logging.Formatter.__init__(self, fmt, datefmt)

	def format(self, record):
		if record.levelno == self.MESSAGE:
			return ' +  ' + str(record.msg).replace('\n', '\n +  ')
		else:
			message = logging.Formatter.format(self, record)

			lines = message.split('\n')

			for i in range(0, len(lines)):
				if i == 0:
					continue
				else:
					lines[i] = '[-] ' + lines[i]

			return '\n'.join(lines)
