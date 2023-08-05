
# Test runners should import a test module and then examine these variables
good_fns = []
bad_fns = []
ugly_fns = []

# Test modules should use these decorators on test cases
# to modify the above variables
def good(fn): # succeeds => good
    good_fns.append(fn.__name__)
    return fn
def bad(fn): # prints to stderr => bad
    bad_fns.append(fn.__name__)
    return fn
def ugly(fn): # runs forever => ugly
    ugly_fns.append(fn.__name__)
    return fn

