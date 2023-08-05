#!/usr/bin/env python
# -*- coding:utf-8 -*-

# TODO: setcmpfunc

import os, sys
import unittest
import pytc

DBNAME = 'test.bdb'
DBNAME2 = 'test.bdb.copy'

class TestBDB(unittest.TestCase):
  def setUp(self):
    if os.path.exists(DBNAME):
      os.remove(DBNAME)

  def testAll(self):
    # new
    db = pytc.BDB()
    # tune
    db.tune(2, 4, 19, 4, 5, pytc.BDBTTCBS)
    # setcache
    db.setcache(1, 1)
    # open
    db.open(DBNAME2, pytc.BDBOWRITER | pytc.BDBOCREAT)
    # copy
    db.copy(DBNAME)
    # close
    db.close
    os.remove(DBNAME2)

    # open
    db = pytc.BDB(DBNAME, pytc.BDBOWRITER)

    # put
    db.put('hamu', 'ju')
    db.put('moru', 'pui')
    db.put('kiki', 'nya-')
    db.put('gunya', 'gorori')

    # get
    self.assertEqual(db.get('hamu'), 'ju')
    # vsiz
    self.assertEqual(db.vsiz('hamu'), len('ju'))

    # putkeep
    self.assertRaises(
      pytc.Error,
      db.putkeep, 'moru', 'puipui')
    db.putkeep('moruta', 'puipui')
    self.assertEqual(db.get('moruta'), 'puipui')

    # putcat
    db.putcat('kiki', 'nya-nya-')
    self.assertEqual(db.get('kiki'), 'nya-nya-nya-')

    # putdup
    db.putdup('kiki', 'unya-n')
    # getlist
    self.assertEqual(db.getlist('kiki'), ['nya-nya-nya-', 'unya-n'])
    # vnum
    self.assertEqual(db.vnum('kiki'), 2)

    # out
    db.out('gunya')
    self.assertRaises(
      pytc.Error,
      db.get, 'gunya')

    # putlist
    db.putlist('gunya', ['gorori', 'harahetta', 'nikutabetai'])
    self.assertEqual(db.getlist('gunya'), ['gorori', 'harahetta', 'nikutabetai'])
    # outlist
    db.outlist('gunya')
    self.assertEqual(db.vnum('gunya'), 0)

    # optimize
    db.optimize(2, 4, 19, 4, 5, pytc.BDBTTCBS)

    # path
    self.assertEqual(db.path(), DBNAME)
    # rnum
    self.assertEqual(db.rnum(), 5)
    # fsiz
    self.assertNotEqual(db.fsiz(), 0)

    # dict like interfaces
    result = []
    for key in db:
      result.append(key)
    self.assertEqual(sorted(result), ['hamu', 'kiki', 'kiki', 'moru', 'moruta'])

    self.assertEqual(sorted(db.keys()),
      ['hamu', 'kiki', 'kiki', 'moru', 'moruta'])
    self.assertEqual(sorted(db.values()),
      ['ju', 'nya-nya-nya-', 'pui', 'puipui', 'unya-n'])
    self.assertEqual(sorted(db.items()),[
      ('hamu', 'ju'), ('kiki', 'nya-nya-nya-'), ('kiki', 'unya-n'),
      ('moru', 'pui'), ('moruta', 'puipui')])

    db['gunya'] = 'tekito'
    self.assertEqual(db['gunya'], 'tekito')
    del db['gunya']
    self.assertRaises(
      pytc.Error,
      db.get, 'gunya')

    self.assert_('hamu' in db)
    self.assert_('python' not in db)

    # curnew
    cur = db.curnew()
    # BDBCUR.first
    cur.first()
    # BDBCUR.key
    self.assertEqual(cur.key(), 'hamu')
    # BDBCUR.val
    self.assertEqual(cur.val(), 'ju')
    # BDBCUR.rec
    self.assertEqual(cur.rec(), ('hamu', 'ju'))
    # BDBCUR.next
    cur.next()
    self.assertEqual(cur.rec(), ('kiki', 'nya-nya-nya-'))
    # BDBCUR.put
    cur.put('fungofungo', pytc.BDBCPCURRENT)
    self.assertEqual(cur.rec(), ('kiki', 'fungofungo'))
    # BDBCUR.out
    cur.out()
    self.assertEqual(db.vnum('kiki'), 1)
    # BDBCUR.prev
    cur.prev()
    self.assertEqual(cur.rec(), ('hamu', 'ju'))
    # BDBCUR.jump
    cur.jump('moru')
    self.assertEqual(cur.rec(), ('moru', 'pui'))
    # BDBCUR.last
    cur.last()
    self.assertEqual(cur.rec(), ('moruta', 'puipui'))

    # tranbegin
    db.tranbegin()
    db.put('moru', 'pupupu')
    self.assertEqual(db.get('moru'), 'pupupu')
    # tranabort
    db.tranabort()
    self.assertEqual(db.get('moru'), 'pui')

    db.tranbegin()
    db.put('moru', 'pupupu')
    # trancommit
    db.trancommit()
    self.assertEqual(db.get('moru'), 'pupupu')

    # vanish
    db.vanish()
    self.assertRaises(
      pytc.Error,
      db.rnum)

    os.remove(DBNAME)

  def testCmpFunc(self):
    db = pytc.BDB()
    # setcmpfunc
    db.setcmpfunc(lambda x,y:len(x) == len(y), 1)
    db.open(DBNAME, pytc.BDBOWRITER | pytc.BDBOCREAT)

    db['kiki'] = 'nya-'
    db['moru'] = 'pui'
    self.assertEqual(db.get('kiki'), 'pui')

    os.remove(DBNAME)

if __name__=='__main__': unittest.main()
