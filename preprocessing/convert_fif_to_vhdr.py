import cca_utils as cca

user = 'kfsh'

print('Subject?')
subj = input('> ')

if subj != 'OP0002':
	block = 'B1'
else:
	block = 'B2'

if user == 'kfsh':
	data_from_server=False

cca.fif_to_vhdr(subj,block,user,data_from_server)