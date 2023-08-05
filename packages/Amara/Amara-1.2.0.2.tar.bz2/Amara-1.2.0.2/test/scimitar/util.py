import os, sys
import tempfile
import cStringIO
from Ft.Xml import CreateInputSource
from amara import scimitar


def run_stron(stron_xml, candidate_xml, legacy_ns=False, phase=None):
    stron_isrc = CreateInputSource(stron_xml)
    candidate_isrc = CreateInputSource(candidate_xml)
    validator_fname = tempfile.mkstemp('.py')[1]
    validator_file = open(validator_fname, 'w')
    scimitar.run(stron_isrc, validator_file, legacy_ns, 1)
    validator_file.close()
    #import popen4
    #(cstdin, cstdout) = os.popen4('/usr/bin/python ' + validator_fname + ' -')
    #cstdin.write(INSTANCE1)
    #result = cstdout.read()
    TEST = 1
    env = {'TEST': 1}
    execfile(validator_fname, env)
    #print >> sys.stderr, validator_fname
    #print >> sys.stderr, env
    validate = env['validate']
    #xmlf = cStringIO.StringIO(candidate_xml)
    result = cStringIO.StringIO()
    validate(candidate_isrc, result, phase=phase)
    os.unlink(validator_fname)
    try:
        os.unlink(validator_fname + 'c')
    except OSError:
        pass
    return result.getvalue()


