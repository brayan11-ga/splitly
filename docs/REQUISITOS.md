# Requisitos del MVP

## Historias de usuario
- HU01: Como organizador, quiero crear un grupo con nombre para controlar gastos del viaje.
- HU02: Como organizador, quiero añadir participantes para asignar quién paga y quién comparte cada gasto.
- HU03: Como participante, quiero registrar un gasto con título, monto, pagador y participantes beneficiados.
- HU04: Como participante, quiero consultar el historial de gastos del grupo.
- HU05: Como participante, quiero ver mi saldo neto para saber si debo pagar o cobrar.
- HU06: Como organizador, quiero ver transferencias sugeridas para liquidar las deudas.
- HU07: Como organizador, quiero editar y eliminar datos de prueba.

## Reglas de negocio
- Montos estrictamente mayores que cero; moneda COP.
- Cada gasto tiene un único pagador que pertenece al grupo.
- El gasto tiene uno o varios participantes beneficiados, todos del grupo.
- Un gasto se distribuye equitativamente entre beneficiados seleccionados.
- Se trabaja en pesos colombianos enteros (amount/amount_owed); los residuos se asignan de forma determinista según UUID ascendente. Esta decisión reemplaza la propuesta anterior de centavos.
- La suma de saldos netos del grupo debe ser cero.
- No se permiten grupos/participantes inexistentes en un gasto.
- Confirmar antes de borrar registros con datos relacionados.

## Criterios de aceptación mínimos
- Crear grupo con 3 personas, registrar dos gastos y comprobar saldos correctos.
- Recargar la página y recuperar los datos desde PostgreSQL.
- Mostrar errores comprensibles para montos inválidos y entidades inexistentes.
- Uso usable en móvil y escritorio.
