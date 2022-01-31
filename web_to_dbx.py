import requests, os, json, dropbox

def url_dbx_upload(url, dbx_path):
	# dbx_path is dropbox folder path
	# dbx_file is the corresponding output file in the dbx_path
	# DON'T mix them up! (It will save you an afternoon of debugging!)
	
	r = requests.get(url, stream=True)	# open url
	file_size = int(r.headers['Content-length'])	# get file_size of 'url'
	file_name = url.split('/')[-1]	# get file name of 'url'
	
	dbx_file		= os.path.join(dbx_path, file_name)	# append 'file_name' to create 'dbx_file'
	dbx_uploaded	= 0									# how much of the current file we have DL'ed
	mode			= dropbox.files.WriteMode.overwrite #dropbox.files.WriteMode.overwrite
	CHUNK_SIZE		= 1 * 1024 * 1024	# 1 MiB Upload chunk size. Can in theory be as high as 150MiB.
	print('file size:', file_size)

	# For smaller files. Cruch in one gulp.
	if file_size <= CHUNK_SIZE:
		dbx.files_upload(r.content, path=dbx_file, mode=mode, autorename=True)
	else:
		init = True	# Set up in loop init logic for DBX cursor. State machines are fun for workarounds.
		for chunk in r.iter_content(chunk_size=CHUNK_SIZE): 	# Chunk upload loop
			if init == True:	# set up DBX cursor. then force continue loop.
				UPLSSR = dbx.files_upload_session_start(chunk)	# UPLoad SSR. For comrade Nikita.
				dbx_uploaded += CHUNK_SIZE
				cursor = dropbox.files.UploadSessionCursor(session_id=UPLSSR.session_id, offset=dbx_uploaded)
				commit = dropbox.files.CommitInfo(path=dbx_file, mode=mode, autorename=True) # !
				init = False
				continue
			# Finish upload session. This terminates the upload_session
			if ((file_size - cursor.offset) <= CHUNK_SIZE): 
				status = dbx.files_upload_session_finish(chunk, cursor, commit)
				dbx_uploaded += file_size - cursor.offset
				cursor.offset = dbx_uploaded
				break
			else:	# Upload full chunk of file.
				dbx.files_upload_session_append_v2(chunk, cursor)
				dbx_uploaded += CHUNK_SIZE		# Keep track of how many bytes we have uploaded.
				cursor.offset = dbx_uploaded	# Update upload cursor with our current file offset.
			print('\rUploaded: ', dbx_uploaded, end='', flush=True)
	return dbx_uploaded
	
with open('dropbox-token.json') as f:
	d = json.load(f)
global dbx
dbx = dropbox.Dropbox(d['token'])

# Dropbox uploads from URLs. ('<our URL to some file>', '<dropbox path>')
# Leave dropbox path as an empty string for uploads to dropbox root.
url_dbx_upload('https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Anas_platyrhynchos_male_female_quadrat.jpg/1200px-Anas_platyrhynchos_male_female_quadrat.jpg', '/Foo/')