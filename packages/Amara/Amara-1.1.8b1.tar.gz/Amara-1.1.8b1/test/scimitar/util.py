import os, sys
import tempfile
import cStringIO
from Ft.Xml import InputSource
from Ft.Lib import Uri
from amara import scimitar


def run_stron(stron_xml, candidate_xml, phase=None):
    isrc_factory = InputSource.DefaultFactory
    stron_isrc = isrc_factory.fromString(stron_xml, 'urn:dummy')
    candidate_isrc = isrc_factory.fromString(candidate_xml, 'urn:dummy')
    validator_fname = tempfile.mkstemp('.py')[1]
    validator_file = open(validator_fname, 'w')
    scimitar.run(stron_isrc, validator_file, 1)
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


def run_stronX(stron_xml, candidate_xml, isrc_factory):
    stron_isrc = isrc_factory.fromString(stron_xml, 'urn:dummy')
    candidate_isrc = isrc_factory.fromString(candidate_xml, 'http://example.com')
    validator_fname = tempfile.mkstemp('.py')[1]
    validator_file = open(validator_fname, 'w')
    scimitar.run(stron_isrc, validator_file, 1)
    validator_file.close()
    #(cstdin, cstdout) = os.popen4('/usr/bin/python ' + validator_fname + ' -')
    #cstdin.write(INSTANCE1)
    #result = cstdout.read()
    TEST = 1
    env = {'TEST': 1}
    execfile(validator_fname, env)
    validate = env['validate']
    #xmlf = cStringIO.StringIO(candidate_xml)
    result = cStringIO.StringIO()
    validate(candidate_isrc, result)
    os.unlink(validator_fname)
    try:
        os.unlink(validator_fname + 'c')
    except OSError:
        pass
    return result.getvalue()


def run_stronY(stron_xml, candidate_xml, isrc_factory):
    stron_isrc = isrc_factory.fromString(stron_xml, 'urn:dummy')
    candidate_isrc = isrc_factory.fromString(candidate_xml, 'urn:dummy')
    validator_fname = tempfile.mkstemp('.py')[1]
    validator_file = open(validator_fname, 'w')
    scimitar.run(stron_isrc, validator_file, 1)
    validator_file.close()
    #(cstdin, cstdout) = os.popen4('/usr/bin/python ' + validator_fname + ' -')
    #cstdin.write(INSTANCE1)
    #result = cstdout.read()
    TEST = 1
    env = {'TEST': 1}
    execfile(validator_fname, env)
    validate = env['validate']
    #xmlf = cStringIO.StringIO(candidate_xml)
    result = cStringIO.StringIO()
    validate(candidate_isrc, result)
    os.unlink(validator_fname)
    try:
        os.unlink(validator_fname + 'c')
    except OSError:
        pass
    return result.getvalue()



