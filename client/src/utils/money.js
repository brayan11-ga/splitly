export const MAX_COP = Number.MAX_SAFE_INTEGER
const formatter = new Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP', maximumFractionDigits: 0 })
export const formatCOP = amount => `${formatter.format(amount)} COP`

// Reject separators, decimals and scientific notation; input stays a string until valid.
export function parseCOP(value) {
  if (!/^\d+$/.test(value)) return null
  const amount = Number(value)
  return Number.isSafeInteger(amount) && amount > 0 ? amount : null
}

export function previewShares(amount, participants) {
  if (!Number.isSafeInteger(amount) || amount <= 0 || participants.length === 0) return []
  const ordered = [...participants].sort((a, b) => a.id < b.id ? -1 : a.id > b.id ? 1 : 0)
  const total = BigInt(amount)
  const count = BigInt(ordered.length)
  const quotient = total / count
  const remainder = total % count
  return ordered.map((member, index) => ({ ...member, amount_owed: Number(quotient + (BigInt(index) < remainder ? 1n : 0n)) }))
}
