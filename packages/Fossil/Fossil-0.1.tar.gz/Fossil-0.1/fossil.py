import dumbdbm as db
import os, sys
from sha import sha

def error(message):
	sys.stderr.write('fsl: %s\n' % message)
	sys.exit(1)

class Storage:
	def __init__(self): self.db = db.open('.fossil')
	def __del__(self):  self.db.close()
	def get_blob(self, hash):
		if not 'blob:' + hash in self.db: return ''
		return self.db['blob:' + hash]
	def set_blob(self, data):
		hash = sha(data).hexdigest()
		self.db['blob:' + hash] = data
		return hash
	def list_blobs(self):
		result = []
		for item in self.db.keys():
			if item.startswith('blob:'):
				item = item.replace('blob:', '', 1)
				result.append(item)
		return result
	def set_tree(self, items):
		data = ''
		for i in items.keys():
			data += i + '\t' + items[i] + '\n'
		hash = sha(data).hexdigest()
		self.db['tree:' + hash] = data
		return hash
	def get_tree(self, hash):
		if not 'tree:' + hash in self.db: return ''
		data = self.db['tree:' + hash]
		result = dict()
		for line in data.split('\n'):
			if not line: break
			file, hash = line.split('\t')
			result[file] = hash
		return result
	def list_trees(self):
		result = []
		for item in self.db.keys():
			if item.startswith('tree:'):
				item = item.replace('tree:', '', 1)
				result.append(item)
		return result
	def set_property(self, name, value):
		self.db['prop:' + name] = value
		return value
	def get_property(self, name):
		if not 'prop:' + name in self.db: return ''
		return self.db['prop:' + name]
	def list_properties(self):
		result = []
		for item in self.db.keys():
			if item.startswith('prop:'):
				item = item.replace('prop:', '', 1)
				result.append(item)
		return result
	def get_commit(self, hash):
		if not 'cmt:' + hash in self.db: return ['', '', '']
		data = self.db['cmt:' + hash].split('\n')
		tree = data[0]
		previous = data[1]
		message = data[2].replace('\\n', '\n')
		return [tree, previous, message]
	def set_commit(self, tree, previous, message, make_top=True):
		data = tree + '\n' + previous + '\n'
		data += message.replace('\n', '\\n')
		hash = sha(data).hexdigest()
		self.db['cmt:' + hash] = data
		if make_top:
			self.set_property('head', hash)
		return hash
	def list_commits(self):
		result = []
		for item in self.db.keys():
			if item.startswith('cmt:'):
				item = item.replace('cmt:', '', 1)
				result.append(item)
		return result

class Middle:
	def __init__(self):
		self.be = Storage()
	def add_file(self, name):
		self.clear_blanks_in_mf()
		files = self.be.get_property('managed-files').split('\n')
		if os.access(name, os.F_OK):
			files.append(name)
		finallist = '\n'.join(files)
		self.be.set_property('managed-files', finallist)
	def del_file(self, name):
		self.clear_blanks_in_mf()
		files = self.be.get_property('managed-files').split('\n')
		for i in files:
			if i == name:
				files.remove(i)
		finallist = '\n'.join(files)
		self.be.set_property('managed-files', finallist)
	def list_files(self):
		self.clear_blanks_in_mf()
		files = self.be.get_property('managed-files').split('\n')
		return files
	def commit(self, message):
		self.clear_blanks_in_mf()
		files = self.be.get_property('managed-files').split('\n')
		hashes = []
		for file in files:
			contents = open(file).read()
			hash = self.be.set_blob(contents)
			hashes.append(hash)
		cmttree = dict()
		for i in range(len(files)):
			cmttree[files[i]] = hashes[i]
		tree = self.be.set_tree(cmttree)
		self.be.set_property('current-tree', tree)
		self.be.set_commit(tree, self.be.get_property('head'), message)
	def clear_blanks_in_mf(self):
		files = self.be.get_property('managed-files').split('\n')
		for i in files:
			if i == '': files.remove(i)
		self.be.set_property('managed-files', '\n'.join(files))
	def extract_tree(self, tree):
		os.mkdir(tree)
		tr = self.be.get_tree(tree)
		for item in tr.keys():
			file, hash = item, tr[item]
			dir = tree + '/' + os.popen('dirname %s' % file).read().strip()
			os.system('mkdir -p %s' % dir)
			data = self.be.get_blob(hash)
			open(tree + '/' + file, 'w').write(data)
		print tree
	def diff_blobs(self, blob1, blob2):
		import difflib
		a = self.be.get_blob(blob1).split('\n')
		b = self.be.get_blob(blob2).split('\n')
		diff = difflib.context_diff(a, b)
		return diff
