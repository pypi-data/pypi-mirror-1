"""Helper functions

Consists of functions to typically be used within templates, but also
available to Controllers. This module is available to templates as 'h'.
"""
# Import helpers as desired, or define your own, ie:
#from webhelpers.html.tags import checkbox, password

from webhelpers.html.tags import stylesheet_link, javascript_link
from routes import url_for
import os, time, subprocess, operator, email, pyme.core
from pyme.constants import protocol, status, sigsum, validity

def filelisting(path, column=0, order=False):
    """ given a path return a tuple (filenames,filesize in kilobytes,last modification time
    """
    filenames = []
    for directory_tuple in os.walk(path):
        for file_entry in directory_tuple[2]:
            fullpath = os.path.join(directory_tuple[0],file_entry)
            container = os.path.split(directory_tuple[0])[1]
            if not os.path.islink(fullpath):
                pretty_mtime = time.strftime("%Y-%d-%m %H:%M",time.localtime(os.path.getmtime(fullpath)))
                mtime = int(os.path.getmtime(fullpath))
                fsize = os.path.getsize(fullpath)
                filenames.append((file_entry,fsize,container,pretty_mtime,mtime,fullpath))
    return sorted(filenames, key=operator.itemgetter(column), reverse=order)

def safefile(repository,path):
    """ given a repository path and a relative attempted access path:
        strips the leading slash, joins, normalizes, and in the case of symlinks
            determines the actual location, of the attempted access path
        if the file is not a symlink and exists below the repository path, returns the calculated path
        else return None (which evaluates to false)
    """
    path = path.lstrip('/\\')
    path = os.path.join(repository,path)
    path = os.path.realpath(os.path.abspath(path))
    if os.path.isfile(path) and not os.path.islink(path):
        if os.path.commonprefix([repository,path]) == repository:
            return path
        else:
            return None
    else:
        return None
    
def decodeMessage(messageString):
    """ given message/rfc822 returns the content
    """
    package = email.message_from_string(messageString)

    message = ""
    for part in package.walk():
        if not part.is_multipart():
            message+=(part.get_payload(decode=True))
    return message

def verify_patch(keyring_dirpath,keyring_basepath,input,required_trust,get_output=False,unicode=True):
    """ verifies a patch and returns results in a tuple
        input:  keyring_dirpath, keyring_basepath: safely joined to form the keyring homedir
                input: input message to verify
                get_output: return verified output, or None
                unicode: convert input message from utf-8 to local encoding
        output, a tuple:
                return_bool: true if verified, false elsewhise
                return_string: accumulated string describing operation
                verified output: optional, verified message or None
    """
    return_bool, return_string, verified_output = False, "", None

    keyring_basepath = keyring_basepath.lstrip('/\\')
    keyring_homedir = os.path.join(keyring_dirpath, keyring_basepath)
    if not os.path.exists(keyring_homedir):
        os.makedirs(keyring_homedir)

    for engine in pyme.core.get_engine_info():
        if engine.protocol == protocol.OpenPGP:
            gpg_executable = engine.file_name
    context = pyme.core.Context()
    context.set_engine_info(protocol.OpenPGP, gpg_executable, keyring_homedir.encode('utf-8'))
    if unicode:
        signature = pyme.core.Data(string=input.encode('utf-8'))
    else:
        signature = pyme.core.Data(string=input)
    plain = pyme.core.Data()
    try:
        context.op_verify(signature,None,plain)
    except pyme.errors.GPGMEError:
        return_string += "Patch is not signed, or improperly signed\n"
    else:
        result = context.op_verify_result()
        if len(result.signatures) != 1:
            return_string += "Expected clearsigned document must have one signature\n"
        else:
            signature = result.signatures[0]
            if signature.status == status.EOF:
                try:
                    current_trust = context.get_key(signature.fpr,0).owner_trust
                except pyme.errors.GPGMEError:
                    current_trust = 0
                if current_trust < required_trust:
                    return_string += "Signature does not have sufficient trust\n"
                else:
                    return_bool = True
                    return_string += "Signature succesfully verified\n"
                    if get_output:
                        plain.seek(0,0)
                        verified_output = plain.read()
            else:
                return_string += match_signature_status(signature.summary)
    if get_output:
        return return_bool, return_string, verified_output
    else:
        return return_bool, return_string

def match_signature_status(summary):
    """ performs bitwise matchings between the gpgme_sigsum_t summary vector
        and the GPGME_SIGSUM_* constants to determine the OpenPGP verification
        status
        outputs the results as a formatted string
    """
    message = "OpenPGP warnings:\n"
    codes = \
        { sigsum.SYS_ERROR: "SYS_ERROR" + ": system error occured"
        , sigsum.BAD_POLICY: "BAD_POLICY" + ": policy requirement not met"
        , sigsum.CRL_TOO_OLD: "CRL_TOO_OLD" + ": certificate revocation list too old"
        , sigsum.CRL_MISSING: "CRL_MISSING" + ": no revocation mechanism available"
        , sigsum.KEY_MISSING: "KEY_MISSING" + ": no matching key/certificate"
        , sigsum.SIG_EXPIRED: "SIG_EXPIRED" + ": signature has expired"
        , sigsum.KEY_EXPIRED: "KEY_EXPIRED" + ": key/certificate has expired"
        , sigsum.KEY_REVOKED: "KEY_REVOKED" + ": key/certificate has been revoked"
        , sigsum.RED: "RED" + ": signature is bad"
        , sigsum.GREEN: "GREEN" + ": signature is fully valid"
        , sigsum.VALID: "VALID" + ": signature is valid"
        }
    for bit_location in codes:
        if bit_location & summary == bit_location:
            message += "  " + codes[bit_location] + "\n"
    message = message.rstrip(", ") + "\n"
    return message

def apply_patch(repository_name,repository_path,patch,command,command_options):
    """ generator object. Given the necessary data, applies a darc patch.
        Yields output throughout the process to keep the user informed in case of exponential merges
    """
    name = repository_name.lstrip('/\\')
    name = name + ".dpatch." + time.strftime("%Y.%d.%m.%H.%M.%S",time.localtime())
    path = os.path.join(repository_path,name)
    try:
        patchFile = open(path,"w")
        try:
            patchFile.write(patch)
        finally:
            patchFile.close()
    except IOError:
        yield "File open failed ::\n"
    else:
        command.append("apply")
        for args in command_options.split(" "):
            if args != '':
                command.append(arg)
        command.append(path.encode('utf-8')) # keep apache mod_wsgi happy, why??
        yield "Using the following command:"
        for item in command:
            yield " " + item
        yield "\n"
        retproc = subprocess.Popen(command,cwd=repository_path,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        proc_communicate = retproc.communicate()
        yield proc_communicate[0]
        os.remove(path)

def quarantine_prune(repository_name,quarantine_path,max_patches,max_size,patch_length):
    """ Removes extra patches on a per-repository basis based on information from parameters
        Several quirks:
            1) will remove a patch in anticipation of a new patch. If subsequent actions fail,
                an extra patch will be removed
            2) possible to upload a large patch to flush all other patches from the quarantine
        Returns None for successful operation or an error message
    """
    if patch_length <= 0:
        return "Not accepting empty patches\n"
    else:
        quarantine_path = os.path.join(quarantine_path,repository_name.lstrip('/\\'))
        quarantine_list = filelisting(quarantine_path,4)

        while(len(quarantine_list) > 0 and len(quarantine_list) >= max_patches):
            os.remove(quarantine_list[0][5])
            del(quarantine_list[0])
        if len(quarantine_list) >= max_patches:
            return "Could not allocate resources to quarantine patch\n"
        else:
            total_size = sum(map(operator.itemgetter(1),quarantine_list))
            total_size = total_size + patch_length
            while(len(quarantine_list) > 0 and total_size > max_size):
                total_size-=quarantine_list[0][1]
                os.remove(quarantine_list[0][5])
                del(quarantine_list[0])
            if total_size > max_size:
                return "Could not allocate resources to quarantine patch\n"
            else:
                return None

def quarantine(repository_name,quarantine_path,patch):
    """ Generator object. Places the darcs patch in the quarantine
        Yields output throughout the process
    """
    quarantine_path = os.path.join(quarantine_path,repository_name.lstrip('/\\'))
    name = "dpatch." + time.strftime("%Y-%d-%m.%H-%M-%S",time.localtime())
    if not os.path.isdir(quarantine_path):
        os.makedirs(quarantine_path)
    quarantine_file = os.path.join(quarantine_path,name)
    try:
        patchFile = open(quarantine_file,"w")
        try:
            patchFile.write(patch)
            yield "Identity not verified, patch written to quarantine\n"
        finally:
            patchFile.close()
    except IOError:
        yield "File open failed ::\n"
