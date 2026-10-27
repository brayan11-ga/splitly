export default async function teardown() {
  // Cierre cooperativo: permite retirar la base temporal antes de taskkill Windows.
  try {
    await fetch('http://127.0.0.1:8001/__test/shutdown', { method: 'POST' })
    for (let attempt = 0; attempt < 40; attempt++) {
      await new Promise(resolve => setTimeout(resolve, 250))
      try { await fetch('http://127.0.0.1:8001/api/health') }
      catch { return }
    }
    throw new Error('La API de pruebas no finalizó correctamente; revisar bases temporales.')
  } catch (error) {
    if (error.message.includes('no finalizó')) throw error
  }
}
