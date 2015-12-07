Scubble
=======

Scubble is a Python based micro language implementation. It is intended as a base for writing DSLs or simple experiments.
It is inspired by code and ideas from Terence Parr's excellent 'Language Implementation Patterns'.

## Features
- Scoped parser and interpreter
- Base syntax allowing for definition of structures and functions

  
## Basic syntax and examples
### Define a simple structure
```
defstruct BaseResource:
  target, call, args
end

defstruct SomeOtherResource:
  alternative_target, blip
end
```
    
### Instantiate a structure instance
```
example = new BaseResource
example.target = 'hello'
example.call = 'on_get'
example.args = 'somearg'

example2 = new BaseResource
example2.target = 'hello2'

someother = new SomeOtherResource
someother.alternative_target = 22
someother.blip = 'blop'

print example
# => <struct>BaseResource fields ['args', 'call', 'target'] values {'args': 'somearg', 'call': 'on_get', 'target': 'hello'} 
print example2
# => <struct>BaseResource fields ['args', 'call', 'target'] values {'target': 'hello2'}
print someother
# => <struct>SomeOtherResource fields ['blip', 'alternative_target'] values {'blip': 'blop', 'alternative_target': 22}
```

### Define a function
```
defun funky_brief(arg1):
  print arg1
end
```

### Call the function
```
funky_brief('brief')
# => brief
```

### Use inner scoping
```
defun funky(arg1, arg2):
  print arg1
  print arg2
  defun inner_funky(arg3):
    print arg3
  end
  inner_funky('inner-works!')
end

funky('test', 'test2')
# => test
# => test2
# => inner-works!
```

### Structure can be passed into function scope
```
defun funky_structure(somestruct):
    print somestruct
end

funky_structure(example)
# => <struct>BaseResource fields ['args', 'call', 'target'] values {'args': 'somearg', 'call': 'on_get', 'target': 'hello'}
```

### Functions have valid return values from their scope
```
defun returner():
  inner_var = 'ill be back'
  return inner_var
end

defun returner_warg(incoming):
  random = 22
  return incoming
end

result = returner()
print result
# => ill be back

print returner_warg('returner_warg')
# => returner_warg
```
