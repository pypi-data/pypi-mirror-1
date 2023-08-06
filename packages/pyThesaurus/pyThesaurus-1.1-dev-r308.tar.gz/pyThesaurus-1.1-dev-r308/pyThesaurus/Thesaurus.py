# begin: Platecom header
# -*- coding: latin-1 -*-
# vim: set ts=4 sts=4 sw=4 :
#
# $Id: Thesaurus.py 308 2008-06-26 17:46:59Z flarumbe $
#
# end: Platecom header

from config import *
from Concept import Concept

def _join_(self, s, l=[]):
	"""
	_join_(object, str, list<str>) -> list<str>

	Get a list of terms@lang in supported languages
	"""
	return [ "%s@%s" % (s, i) for i in l if l in self._lang ]

def _split_(self, s):
	"""
	_split_(object, str) -> str, str

	Separe the term and the language from the string
	"""
	return s.split("@")

class Thesaurus:
	def __init__(self, lang=[], TDict=dict, TList=list):
	   """
	   __init__(object) -> Thesurus

	   Init the Thesaurus.
	   """
	   self._dict = TDict
	   self._list = TList
	   self._concept = self._dict()
	   self._term = self._dict()
	   self._context = self._dict()
	   self._last_concept_id = -1 
	   self._lang = self._list()

	def get_prefered(self, t, lang=[], contexts=None):
		"""
		get_prefered(object, str, list<str>) -> list<str>

		Return prefered terms of term t in all languages in lang. If lang is [] return all terms.
		"""
		cs = self(t, contexts)

		ts = []

		for c in cs:
		  ts += self._concept[c].get_prefered(lang)

		return ts

	def set_prefered(self, t, cid):
		"""
		set_prefered(object, str, cid) -> None

		Set the prefered term t in some language in concept cid
		"""
		self._concept[cid].set_prefered(t)

	def get_equivalent(self, t, lang=[], contexts=None, exclude = False):
		"""
		get_equivalent(object, str, list<str>) -> list<str>

		Return equivalent terms of term t in all languages in lang. If lang is [] return all terms.
		"""
		cid = self(t, contexts)

		ts = []
		for c in cid:
			ts += self[c]['=']

		ts = dict([ ("%s@%s" % (_t,_l), None) for _t,_l in [ t_.split('@') for t_ in ts ] if _l in lang ]).keys()

		if exclude and t in ts:
			ts.remove(t)

		return ts

	def get_similars(self, t, lang=[], contexts=None):
		"""
		get_similars(object, str, list<str>) -> list<str>

		Return similar terms of term t in all languages in lang. If lang is [] return all terms.
		"""
		cid = self(t, contexts)

		ts = []
		for c in cid:
			ts += self[c]['~']

		ts = dict([ ("%s@%s" % (t,l), None) for t,l in [ t.split('@') for t in ts ] if l in lang ]).keys()

		return ts

	def get_broader(self, t, lang=[], contexts=None):
		"""
		get_broader(object, str, list<str>) -> list<str>

		Return broaders terms of term t in all languages in lang. If lang is [] return all terms.
		"""
		cid = self(t, contexts)

		ts = []
		for c in cid:
			ts += self[c]['<']

		ts = dict([ ("%s@%s" % (t,l), None) for t,l in [ t.split('@') for t in ts ] if l in lang ]).keys()

		return ts

	def get_narrower(self, t, lang=[], contexts=None):
		"""
		get_narrower(object, str, list<str>) -> list<str>

		Return narrower terms of term t in all languages in lang. If lang is [] return all terms.
		"""
		cid = self(t, contexts)

		ts = []
		for c in cid:
			ts += self[c]['>']

		ts = dict([ ("%s@%s" % (t,l), None) for t,l in [ t.split('@') for t in ts ] if l in lang ]).keys()

		return ts

	def get_related(self, t, lang=[], exclude=True, contexts=None):
		"""
		get_related(object, str, list<str>) -> list<str>

		Return related terms of term t in all languages in lang. If lang is [] return all terms.
		"""
		cid = self(t, contexts)

		ts = []
		hidden = False
		for c in cid:
			ts += self[c]['-']
			hidden = hidden or t in self[c]['#']

		ts = dict([ ("%s@%s" % (_t,_l), None) for _t,_l in [ t_.split('@') for t_ in ts ] if _l in lang ]).keys()

		if exclude or hidden:
			return ts
		else:
			return ts + [ t ]

	def get_concepts(self, ts, contexts=None):
		"""
		get_concepts(object, list<str>) -> int

		Return the concepts id associated to all terms in ts.
		"""
		cid = []
		for t in ts:
			cid += self(t, contexts)

		return dict([ (c, None) for c in cid ]).keys()

	def get_publicNotes(self, c):
		"""
		get_publicNotes(object, int) -> dict

		Return the dict of public notes of a concept.

		get_publicNotes(c).keys() =	[ 'definition', 'scopeNote', 'example', 'historyNote', 'class' ]
		get_publicNotes(c)[x].keys() = [ 'value', 'date', 'creator' ]
		"""
		return self[c]._pubn

	def get_privateNotes(self, c):
		"""
		get_privateNotes(object, int) -> dict

		Return the dict of private notes of a concept.

		get_privateNotes(c).keys() = [ 'editorialNote', 'changeNote' ]
		get_privateNotes(c)[x].keys() = [ 'value', 'date', 'creator' ]
		"""
		return self[c]._privn

	def terms(self, contexts=None):
		"""
		terms(object) -> list<str>

		Return the list of terms of the thesauro
		"""
		return self._term.keys()

	def concepts(self, contexts=None):
		"""
		terms(object) -> list[int]

		Return the list of concepts id of the thesaurus
		"""
		return self._concept.keys()

	def concepts_objects(self, contexts=None):
		"""
		terms(object) -> list[object]

		Return the list of concepts of the thesaurus
		"""
		return self._concept.values()

	def contexts(self):
		"""
		contexts(object) -> list<str>

		Return a list of classes.
		"""
		return self._context.keys()

	def search_term(self, str, contexts=None):
		"""
		search_term(str) -> list<str>

		Return a list of similar terms to the str
		"""
		import re
		cre = re.compile(str)

		return [ k for k in self._term.keys() if cre.search(k) ]

	def __getitem__(self, idx):
		"""
		__getitem__(object, int) -> dict

		Return the concept dict of idx.

		__getitem__(idx).keys() = [ '=', '#', '<', '>', '-', '~', concept_id... ] 
		if c not defined(object, raise IndexError, 'not defined'
		"""
		if idx in self._concept:
		   return self._concept[idx]
		else:
		   raise IndexError, 'not defined'

	def __call__(self, t, contexts=None):
		"""
		__call__(object, str) -> list<int>

		Return the concept id of the term.

		if t not defined(object, raise IndexError, 'not defined'
		"""
		if t in self._term:
			return [ c for c in self._term[t] if contexts==None or contexts==[] or sum([ xc==xi for xc in self._concept[c]._contexts for xi in contexts ])]
		else:
			raise IndexError, 'not defined'

	def append_term(self, t, et=[], ht=[], net=[], bt=[], nt=[], rt=[], st=[], contexts=None, automatic=False):
		"""
		append_term(object, str, int, et=list<str>, ht=list<str>, net=list<str>, bt=list<str>,
							 nt=list<str>, rt=list<str>,  st=list<str>, automatic=bool,
							 contexts=list<str>) -> None

		Add a new term t of class c with the following relations.
		"""
		append_concept_id = Concept(et=[t] + et, ht=ht, net=net, bt=bt, nt=nt, st=st, rt=rt, contexts=contexts)
		old_concept_at = self._previous_concept_to_join(append_concept_id)
		if old_concept_at is None:
			self.append_concept(append_concept_id)
		else:
			if automatic:
				self.replace_concept_at(self[old_concept_at].join_to(append_concept_id), old_concept_at)
			else:
				raise ConceptsConflic, old_concept_at

	def _previous_concept_to_join(self, append_concept, M=matrix_comparation, S=minimum_score):
		"""
		_previous_concept_to_join(object, Concept, M=list<list<int>>, S=int) -> int

		Return the most equal concept in the thesaurus.
		"""
		for idx in self._concept:
			if append_concept.could_be_joined_to(self[idx], M, S): return idx
		return None

	def append_concept(self, c):
		"""
		append_concept(object, Concept) -> Id

		Add a new concept to the Thesaurus, and return the concept id.
		"""
		self._last_concept_id += 1
		self._concept[self._last_concept_id] = c
		for context in c.contexts():
			if not context in self._context: self._context[context] = self._list()
			self._context[context].append(self._last_concept_id)
		self._terms_belong_to_concept(c['='] + c['#'], self._last_concept_id)
		return self._last_concept_id

	def replace_concept_at(self, concept, idx):
		"""
		replace_concept_at(object, Concept, int) -> None

		Replaces the concept with idx id with the new concept concept.
		"""
		self._concept[idx] = concept
		self._terms_belong_to_concept(concept.et, idx)

	def _terms_belong_to_concept(self, terms, concept_idx):
		"""
		_terms_belong_to_concept(list<str>, int) -> None

		Associate terms belongs to concept concept_idx.
		"""
		for t in terms:
			if t in self._term:
				if concept_idx not in self._term[t]:
					self._term[t].append(concept_idx)
			else:
				self._term[t] = [concept_idx]

	def get_terms_of_context(self, context):
		"""
		get_terms_of_context(object, context) -> list<str>

		Return the terms of a context.
		"""
		result = []
		for concept_id in self._context[context]:
			concept = self._concept[concept_id]
			result.append(concept['='])
		return result

	def term_concepts(self, term, context=None):
		return self.concepts_from_ids(self.term_concepts_ids(term, context))

	def term_concepts_ids(self, term, context=None):
		return self.get_concepts([term], context)

	def concepts_search(self, search_expression, context=None):
		import re
		try:
			reg = re.compile(search_expression, re.IGNORECASE)
		except:
			raise KeyError, "Invalid search expression: %s\n%s" % (search_expression, sys.exc_value)
		return [ (cid, self[cid]) for cid in self.concepts() if self[cid].match(reg) ]

	def concepts_search_ids(self, search_expression, context=None):
		return [ cid for (cid, concept) in self.concepts_search(search_expression, context) ]

	def concepts_search_objects(self, search_expression, context=None):
		return [ concept for (cid, concept) in self.concepts_search(search_expression, context) ]

	def concepts_from_ids(self, cids):
		return [ self[cid] for cid in cids ]

	def query( self, search_expression,
		narrowedthan = None, borrowedthan = None, contexts = [], languages = [],
		inbranch = None, hidden = None, max_results = 5 ):
		"""
		Return terms in regexp, between 'borrowedthan' and 'narrowedthan' terms, in defined contexts. If inbrach is a list of terms, then returned terms are in the same branch of these. Dont return terms in except. The precedence is (TODO):
            1) Concepts whose prefered term starts with search_expression.
            2) Concepts whose prefered term has a word starting with search_expression.
            3) Concepts whose prefered term has search_expression inside.
            4) Concepts whose equivalent terms has search_expression inside.

		context == None: accept terms in all contexts.
		narrowedthan == None: no limits on top of thesaurus.
		borrowedthan == None: no limits on bottom of thesaurus.
		inbranch == None: all terms.
		except == None: all terms.

		@regexp: Regular expresion.
		@narrowedthan: List of terms.
		@borrowedthan: List of terms.
		@contexts: List of contexts.
		@inbranch: List of terms.
		@except: List of terms.
		@return: List of terms.

		>>> T.query('B.*', narrowedthan=['Tierra'], borrowedterm=None, contexts=['geographic']
								inbranch=['America'], except=None)
		[ ... 'Bogota', 'Buenos Aires', 'Bolivia', ... ]

		>>> T.query('B.*', narrowedthan=['Escritor', 'America'],
								borrowedterm=None, contexts=['geographic', 'literatura']
								inbranch=['Argentina'], except=['Borges']
		[ ... 'Cortaza', 'Sabato' ... ]

		"""
		conceptsResults = self.concepts_search(search_expression, contexts)
		return [ (conceptsResults[index][1].get_prefered(languages)[0], conceptsResults[index][0]) for index in range(min(len(conceptsResults), max_results)) ]
