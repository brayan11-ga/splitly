import { test } from 'node:test'
import assert from 'node:assert/strict'
import { MAX_COP, parseCOP, previewShares } from '../src/utils/money.js'

test('COP input accepts safe positive integers only', () => {
  assert.equal(parseCOP('90000'), 90000)
  assert.equal(parseCOP(String(MAX_COP)), MAX_COP)
  for (const value of ['', '0', '-1', '1.5', '90.000', '1e3', '9007199254740992']) assert.equal(parseCOP(value), null)
})

test('preview uses stable UUID order and preserves every peso', () => {
  const participants = [{ id: 'c', name: 'C' }, { id: 'a', name: 'A' }, { id: 'b', name: 'B' }]
  assert.deepEqual(previewShares(101, participants).map(share => share.amount_owed), [34, 34, 33])
  assert.deepEqual(previewShares(101, participants), previewShares(101, [...participants].reverse()))
  for (const amount of [1, 101, 90000, MAX_COP]) {
    const result = previewShares(amount, participants)
    assert.equal(result.reduce((sum, share) => sum + share.amount_owed, 0), amount)
  }
})
