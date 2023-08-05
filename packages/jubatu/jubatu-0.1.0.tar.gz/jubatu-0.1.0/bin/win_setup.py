import os,sys

desktopShortcut=os.path.join(get_special_folder_path("CSIDL_COMMON_DESKTOPDIRECTORY"),'Jubatu.lnk')
prog = os.path.join(os.path.dirname(sys.argv[0]),'jubatu')
print "Executing", prog

create_shortcut("pythonw", 'Jubatu', desktopShortcut, prog)
file_created(desktopShortcut)
print "Created icon on desktop"

programsMenuDir=os.path.join(get_special_folder_path("CSIDL_COMMON_PROGRAMS"), 'Jubatu')
programsShortcut=os.path.join(programsMenuDir, 'Jubatu.lnk')

if not os.path.exists(programsMenuDir):
    os.mkdir(programsMenuDir)   
directory_created(programsMenuDir)

create_shortcut("pythonw", 'Jubatu', programsShortcut, prog)
file_created(programsShortcut)
print "Created entry in the programs list"
    