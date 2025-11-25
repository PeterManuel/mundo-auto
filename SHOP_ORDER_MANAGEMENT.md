# Sistema de Gestão de Pedidos por Loja

Este documento descreve as funcionalidades implementadas para gestão de pedidos por loja no sistema MundoAuto.

## Funcionalidades Implementadas

### 1. Visualizar Todos os Pedidos de uma Loja

**Endpoint:** `GET /api/v1/shops/{shop_id}/orders`

**Parâmetros de consulta:**
- `status` (opcional): Filtrar por status do pedido (pending, processing, shipped, delivered, cancelled)
- `customer_id` (opcional): Filtrar por ID do cliente
- `skip`: Número de registros para pular (paginação)
- `limit`: Número máximo de registros a retornar

**Exemplo de uso:**
```
GET /api/v1/shops/123e4567-e89b-12d3-a456-426614174000/orders?status=pending&limit=50
```

### 2. Atualizar Status dos Pedidos

**Endpoint:** `PUT /api/v1/shops/{shop_id}/orders/{order_id}/status`

**Transições de status permitidas:**
- `PENDING` → `PROCESSING` ou `CANCELLED`
- `PROCESSING` → `SHIPPED` ou `CANCELLED`
- `SHIPPED` → `DELIVERED` ou `RETURNED`
- `DELIVERED` → `RETURNED`

**Corpo da requisição:**
```json
{
  "status": "processing",
  "comment": "Pedido sendo preparado para envio"
}
```

### 3. Consultar Histórico de Pedidos por Cliente

**Endpoint:** `GET /api/v1/shops/{shop_id}/customers/{customer_id}/orders`

**Parâmetros:**
- `shop_id`: ID da loja
- `customer_id`: ID do cliente
- `skip`, `limit`: Paginação

**Retorna:**
- Informações do cliente
- Total de pedidos realizados
- Total gasto
- Data do último pedido
- Lista de pedidos

## Endpoints Adicionais

### 4. Resumo de Pedidos da Loja

**Endpoint:** `GET /api/v1/shops/{shop_id}/orders/summary`

**Retorna:**
- Total de pedidos
- Pedidos por status
- Receita total
- Estatísticas gerais

### 5. Informações de um Pedido Específico

**Endpoint:** `GET /api/v1/shops/{shop_id}/orders/{order_id}`

**Retorna:** Informações completas do pedido com itens e histórico de status.

### 6. Atualizar Status de Pagamento

**Endpoint:** `PUT /api/v1/shops/{shop_id}/orders/{order_id}/payment`

**Corpo da requisição:**
```json
{
  "payment_status": "paid"
}
```

### 7. Atualizar Informações de Envio

**Endpoint:** `PUT /api/v1/shops/{shop_id}/orders/{order_id}/shipping`

**Parâmetros:**
- `tracking_number`: Número de rastreamento
- `shipping_company`: Empresa de transporte

### 8. Listar Clientes da Loja

**Endpoint:** `GET /api/v1/shops/{shop_id}/customers`

**Retorna:** Lista de clientes que fizeram pedidos na loja com estatísticas.

### 9. Analytics da Loja

**Endpoint:** `GET /api/v1/shops/{shop_id}/analytics`

**Parâmetros opcionais:**
- `start_date`: Data de início para análise
- `end_date`: Data de fim para análise

**Retorna:**
- Pedidos por status
- Receita total
- Valor médio dos pedidos
- Pedidos por dia (últimos 30 dias)

## Controle de Acesso

O sistema implementa controle de acesso baseado em função:

- **SUPERADMIN**: Acesso a todas as lojas
- **ADMIN**: Acesso a todas as lojas
- **LOGIST**: Acesso apenas à loja atribuída (`shop_id` no perfil do usuário)
- **CUSTOMER**: Sem acesso aos endpoints de gestão

## Schemas de Dados

### OrderResponse
Resposta completa do pedido com itens e histórico.

### OrderFilter
Filtros para consulta de pedidos.

### OrderStatusUpdate
Atualização de status com comentário opcional.

### ShopOrderSummary
Resumo estatístico dos pedidos da loja.

### CustomerOrderHistory
Histórico completo de pedidos de um cliente.

## Exemplos de Uso

### 1. Visualizar pedidos pendentes de uma loja
```bash
curl -X GET "http://localhost:8000/api/v1/shops/your-shop-id/orders?status=pending" \
  -H "Authorization: Bearer your-token"
```

### 2. Atualizar status de um pedido
```bash
curl -X PUT "http://localhost:8000/api/v1/shops/your-shop-id/orders/order-id/status" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"status": "processing", "comment": "Pedido em preparação"}'
```

### 3. Ver histórico de um cliente
```bash
curl -X GET "http://localhost:8000/api/v1/shops/your-shop-id/customers/customer-id/orders" \
  -H "Authorization: Bearer your-token"
```

### 4. Obter resumo da loja
```bash
curl -X GET "http://localhost:8000/api/v1/shops/your-shop-id/orders/summary" \
  -H "Authorization: Bearer your-token"
```

## Considerações Técnicas

1. **Performance**: As consultas usam JOINs otimizados e índices adequados.
2. **Segurança**: Validação de acesso em todos os endpoints.
3. **Paginação**: Implementada em todas as listagens.
4. **Validação**: Status transitions são validados.
5. **Auditoria**: Histórico de mudanças de status é mantido.

O sistema está pronto para uso em produção e pode ser estendido com funcionalidades adicionais conforme necessário.