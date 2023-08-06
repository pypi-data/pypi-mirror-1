#!/usr/bin/env python
import re
import sys
from optparse import OptionParser

class OpenStruct(object):
	"""
	A hash-like structure that allows you to get elements with acessors
	(the hash / dict itself can be accessed via self._dict)
	"""
	def __init__(self, h=None):
		if h is None:
			h = {}
		object.__setattr__(self, '_dict', h)

	def __setattr__(self, attr, val):
		if hasattr(self, attr):
			object.__setattr__(self,attr,val)
		else:
			self._dict[attr] = val
	
	def __getattr__(self, attr):
		try:
			return object.__getattribute__(self, '_dict')[attr]
		except KeyError:
			raise AttributeError
	
	def __getitem__(self, attr):
		return object.__getattribute__(self, '_dict')[attr]
		
	def __contains__(self,attr):
		return attr in self._dict
	
	def __setitem__(self, attr, val):
		self._dict[attr] = val
	

class LogicalError(RuntimeError):
	pass

def take_while(func, lst):
	"""
	return the slice of the list from the start to where func(item) first returns False
	"""
	new_lst = []
	for item in lst:
		if func(item):
			new_lst.append(item)
		else:
			break
	return new_lst

def taker_while(func, lst):
	"""
	much like take_while, but the list slice is taken from the end of lst
	"""
	return list(reversed(take_while(func, reversed(lst))))
	
def collapse_list(lst):
	"""
	Deletes all adjacent duplicates in a list
	"""
	if len(lst) < 1: return lst
	last_elem = lst[0]

	new_lst = [last_elem] # initialise with the first element, since it can't be a dupe
	for elem in lst:
		if elem != last_elem:
			new_lst.append(elem)
		last_elem = new_lst
	return new_lst
	

class Mandy(object):
	def __init__(self, autorun = True):
		self.__args = []
		self.__opts = []
		
		self.opts = OpenStruct() # user-visible options
		
		if autorun:
			self.configure()
			self._parse()
			self.__run()
	
	def _parse(self, argv = None):
		if argv is None:
			argv = sys.argv[1:]
		self.__parse(argv)
		self.__args = self.__opts = None  # allow GC
	
	def __run(self):
		exit_code = self.run()
		if exit_code is None:
			exit_code = 0
		sys.exit(exit_code)
	
	def opt(self, name, t=str, short=None, long=None, default=None, optional=False, action=None, desc=None, explicit=False):
		"""
		adds -[short], --[long] and --no-[long] unless short / long is None
		type is cast accordingly for int, float and bool
		(bool is a special case, it allows on/off, true/false, yes/no, 1/0)
		"""
		if t == bool and not explicit:
			nargs = 0 # just consume the flag
		else:
			nargs = 1 # consume flag & value
		if short == None and long == None:
			raise LogicalError, \
				"You must supply either a short option string or a long option string.\n" + \
				"For positional arguments, use this.arg()"
		self.__opts.append(self.__create_option_hash(name=name, type_=t, short=short, long=long, default=default, optional=optional, action=action, desc=desc, nargs=nargs))
	
	def arg(self, name, t=str, short=None, long=None, default=None, optional=False, action=None, desc=None):
		"""
		appends "name" to the list of unnamed arguments
		raises LogicalError if the optional ags are not up one end of the argument list
		i.e. you can have:
		   arg1 arg2 [optional1] [optional2]
		or:
		   [optional1] [optional2] arg1 arg2
		or even:
		   arg1 [optional1] [optional2] arg2
		but you cannot have any mandatory argument with a optional argument on both sides
		"""
		optionality_slices = collapse_list([a['optional'] is True for a in self.__args] + [optional])
		# 2 or less can never be invalid
		# 3 can *only* be valid if it's [mandatory, optional, mandatory]
		# 4 or more is always invalid
		if len(optionality_slices) > 2 and optionality_slices != [False, True, False]:
			raise LogicalError, "Adding %s argument (%s) makes the arguments ambiguous to parse" % ("an optional" if optional else "a mandatory", name)
		
		self.__args.append(self.__create_option_hash(name=name, type_=t, default=default, optional=optional, action=action, desc=desc))

	# -----
	
	__true_s  = ['true','yes','1','on' ]
	__false_s = ['true','no', '0','off']
	
	__true_s_re = [re.compile(regex, re.IGNORECASE) for regex in __true_s]
	__bool_s_re = [re.compile(regex, re.IGNORECASE) for regex in __true_s + __false_s]

	def __is_bool(self, val):  return any([regex.match(val) for regex in self.__bool_s_re ])
	def __is_true(self, val):  return any([regex.match(val) for regex in self.__true_s_re ])
	
	def __convert(self, val, type_, option_string):
		"""
		default conversion function for arbitrary argument types
		"""
		print "val from optparse is %r" % (val,)
		if type_ == bool:
			if val is None and len(option_string) > 2: # TODO: is this what we get from opt_parsey?
				return not option_string.startswith('--no-')
			if not self.__is_bool(val):
				self.__usage("%r is not a boolean" % (val,))
			else:
				return self.__is_true(val)
		else:
			try:
				val = type_(val)
				return val
			except TypeError, e:
				self.__usage("%r could not be converted to a %s:\n%s" % (val, type_.__name__, e.message))

	def __create_option_hash(self, **kw):
		"""
		ensures that any missing values are specified as None,
		and validates that options are sane
		"""
		for key in ['optional', 'name', 'type_']:
			if not key in kw:
				raise LogicalError, "%s is required" % (key,)

		if kw['optional'] is not True and kw['optional'] is not False:
			raise LogicalError, "optional must be set to either True or False"

		# default values
		for key in ['short','long','default', 'action','desc']:
			if key not in kw.keys():
				kw[key] = None
		if kw['optional'] and kw['type_'] == bool and kw['default'] is None:
			kw['default'] = False
		if kw['default'] is not None and kw['optional'] is False:
			raise LogicalError, "default should be None for mandatory options"

		if kw['optional']:
			# initialise default
			self.opts[kw['name']] = kw['default']

		return kw
	
	def __parse(self, argv):
		self.__parser = OptionParser(usage=self.__banner())
		self.opts = OpenStruct()
		
		for option_hash in self.__opts:
			print "adding opt: %r" % (option_hash,)
			opt_strs = []
			if option_hash['short']: opt_strs.append( '-' + option_hash['short'])
			if option_hash['long']:  opt_strs.append('--' + option_hash['long'] )
			
			nargs = option_hash['nargs']
			kwargs = {
				'action':'callback',
				'callback':self.__process_option_callback,
				'callback_args':(option_hash,),
				'nargs': nargs}
			# optparse has funky behaviour here:
			# if type is explicitly set to string (the default),
			# it makes help text like --val=VAL. Whereas if left
			# to the default, it just uses --val. The latter
			# happens to be what we want whenever nargs == 0
			if nargs > 0:
				kwargs['type'] = 'string'
			kwargs['help'] = option_hash['desc'] or ""
			if len(opt_strs) < 1:
				raise LogicalError, "Must have either a short or long identifier"
			print "Adding option: %r / %r" % (opt_strs, kwargs)
			self.__parser.add_option(*opt_strs, **kwargs)
			
			if option_hash['type_'] == bool and option_hash['long'] is not None:
				kwargs['help'] = ''
				self.__parser.add_option('--no-' + option_hash['long'], **kwargs)
		
		(_, remaining_args) = self.__parser.parse_args(argv)
		self.__process_positional_args(remaining_args)
		self.__post_validate_all_args()
		self.__parser = self.__parser.destroy()
	
	def __process_option_callback(self, option_object, option_str, value, parser, option_hash):
		self.__process_option(option_hash, value, option_str)

	def __process_option(self, option_hash, value, option_str):
		print "called back with %r for option hash %r" % (value, option_hash)
		print "option_str = %r" % (option_str,)

		if value == (): # this is how optparse delivers "no arguments"
			value = None
		value = self.__convert(value, option_hash['type_'], option_str)
		if option_hash['action']:
			retval = option_hash['action'](value)
			if retval is not None:
				# action returned something
				value = retval
		self.opts[option_hash['name']] = value
	
	def __positional_arg_description(self):
		def stringize(option_hash):
			arg = option_hash['name']
			if option_hash['optional']:
				arg = '[%s]' % (arg,)
			return arg
		print ' '.join(map(stringize, self.__args))
		return ' '.join(map(stringize, self.__args))
			
	def __process_positional_args(self, args):
		print "parsing positional arguments..."
		
		mandatory = lambda x: x['optional'] is False
		optional = lambda x: x['optional'] is True
		
		start_args = take_while(mandatory, self.__args)
		optional_args = filter(optional, self.__args)
		if start_args == self.__args:
			# don't double-count args if they're all mandatory
			end_args = []
		else:
			end_args = taker_while(mandatory, self.__args)
		
		num_start_args = len(start_args)
		num_end_args = len(end_args)
		num_given_args = len(args)
		num_mandatory_args = num_start_args + num_end_args

		if num_given_args < num_mandatory_args:
			self.__usage("Too few arguments provided (received %s, required %s)" % (len(args), num_mandatory_args))

		if num_given_args > len(self.__args):
			self.__usage("Too many arguments provided (you gave %s, but the maximum allowed is %s)" % (len(args), len(self.__args)))

		start_arg_values = args[:num_start_args]
		end_arg_values = args[:0 - num_end_args]
		optional_arg_values = args[num_start_args:(num_given_args - num_end_args)]
		
		def assign_set(args, values):
			print "assigning %s positional args (of %s)" % (len(values), len(args))
			for i in range(0, len(values)):
				print "processing position arg %s with value %r" % (i, values[i])
				self.__process_option(args[i], values[i], None)
		
		assign_set(start_args, start_arg_values)
		assign_set(end_args, end_arg_values)
		assign_set(optional_args, optional_arg_values)
		
	def __post_validate_all_args(self):
		for option_hash in self.__opts + self.__args:
			if option_hash['name'] not in self.opts:
				if option_hash['optional']:
					# ensure there are no missing keys
					print "nulling it!"
					self.opts[option_hash['name']] = None
				else:
					self.__usage("required argument (%s) was not supplied" % (option_hash['name'],))
			
	
	def __banner(self):
		banner = 'Usage: %prog '
		if not len(self.__opts) == 0:
			banner += '[options] '
		banner += self.__positional_arg_description()
		return banner
	
	def __usage(self, msg=None):
		self.__parser.print_help(sys.stderr)
		print
		if msg is not None:
			print >> sys.stderr, "Error: %s" % (msg,)
		exit(1)
		raise Exception
	

class Doit(Mandy):
	def configure(self):
		self.opt('test', bool, long='test', desc="Frobnicate")
		self.opt('debug', bool, short='d', explicit=True, desc="Set Debug mode")
		self.arg('foo')
		self.arg('moo', optional=True)
		self.arg('moot')
	
	def run(self):
		print self.opts.moo
		print repr(self.opts)

if __name__ == '__main__': Doit()