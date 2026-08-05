// Format decimals nicely: 0.5 → ½, 0.25 → ¼, 0.75 → ¾, else nearest eighth
const FRACTIONS = [
  [1 / 8, '⅛'],
  [1 / 4, '¼'],
  [1 / 3, '⅓'],
  [3 / 8, '⅜'],
  [1 / 2, '½'],
  [5 / 8, '⅝'],
  [2 / 3, '⅔'],
  [3 / 4, '¾'],
  [7 / 8, '⅞'],
]

export function formatAmount(val) {
  if (val == null) return ''

  const whole = Math.floor(val)
  const decimal = val - whole

  // Close enough to a whole number
  if (decimal < 0.05) return `${whole || ''}`
  if (decimal > 0.95) return `${whole + 1}`

  // Find the closest fraction
  let closest = FRACTIONS[0]
  let minDiff = Math.abs(decimal - FRACTIONS[0][0])

  for (const f of FRACTIONS) {
    const diff = Math.abs(decimal - f[0])
    if (diff < minDiff) {
      minDiff = diff
      closest = f
    }
  }

  return whole > 0 ? `${whole} ${closest[1]}` : closest[1]
}
