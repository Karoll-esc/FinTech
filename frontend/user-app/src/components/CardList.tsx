/**
 * CardList Component - Vista de Tarjetas del Usuario
 * TASK-041 a TASK-050: Componente React para HU-015
 * 
 * Muestra lista de tarjetas con:
 * - Últimos 4 dígitos enmascarados
 * - Saldo formateado
 * - Estado visual (color)
 * - Ícono por tipo (Débito/Crédito)
 * - Responsive grid
 */
import { useState, useEffect } from 'react';

interface Card {
  id: string;
  card_number: string;
  card_type: 'DEBIT' | 'CREDIT';
  balance: string;
  status: 'ACTIVE' | 'BLOCKED' | 'SUSPENDED';
  nickname?: string;
  created_at: string;
}

interface CardsResponse {
  cards: Card[];
}

export const CardList = () => {
  const [cards, setCards] = useState<Card[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchCards();
  }, []);

  const fetchCards = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/v1/cards', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Error al cargar tarjetas');
      }

      const data: CardsResponse = await response.json();
      setCards(data.cards);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
    } finally {
      setLoading(false);
    }
  };

  const formatBalance = (balance: string): string => {
    const num = parseFloat(balance);
    return new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(num).replace('COP', '$');
  };

  const maskCardNumber = (lastFour: string): string => {
    return `****${lastFour}`;
  };

  const getStatusClass = (status: string): string => {
    switch (status) {
      case 'ACTIVE':
        return 'status-active';
      case 'BLOCKED':
        return 'status-blocked';
      case 'SUSPENDED':
        return 'status-suspended';
      default:
        return '';
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div data-testid="loading-spinner" className="spinner">
          Cargando tarjetas...
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4">
        <p className="text-red-600 mb-4">Error al cargar tarjetas</p>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={fetchCards}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Reintentar
        </button>
      </div>
    );
  }

  // Empty state
  if (cards.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen p-4">
        <h2 className="text-2xl font-bold mb-2">No tienes tarjetas registradas</h2>
        <p className="text-gray-600 mb-6">Agrega tu primera tarjeta para realizar transferencias</p>
        <button className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700">
          Agregar Primera Tarjeta
        </button>
      </div>
    );
  }

  // Main view with cards
  const hasMaxCards = cards.length >= 3;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Mis Tarjetas</h1>

      {/* Grid de tarjetas */}
      <div 
        data-testid="cards-container" 
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6"
      >
        {cards.map((card) => {
          const isZeroBalance = parseFloat(card.balance) === 0;
          
          return (
            <div
              key={card.id}
              data-testid="card-item"
              className={`
                p-6 rounded-lg shadow-lg border-2
                ${getStatusClass(card.status)}
                ${card.status === 'ACTIVE' ? 'border-green-500 bg-green-50' : ''}
                ${card.status === 'BLOCKED' ? 'border-red-500 bg-red-50' : ''}
                ${card.status === 'SUSPENDED' ? 'border-yellow-500 bg-yellow-50' : ''}
              `}
            >
              {/* Header con tipo de tarjeta */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  {card.card_type === 'DEBIT' && (
                    <span data-testid="debit-icon" className="text-2xl">💳</span>
                  )}
                  {card.card_type === 'CREDIT' && (
                    <span data-testid="credit-icon" className="text-2xl">💎</span>
                  )}
                  <span className="font-semibold">{card.card_type}</span>
                </div>
                <span className={`
                  px-2 py-1 rounded text-xs font-bold
                  ${card.status === 'ACTIVE' ? 'bg-green-200 text-green-800' : ''}
                  ${card.status === 'BLOCKED' ? 'bg-red-200 text-red-800' : ''}
                `}>
                  {card.status}
                </span>
              </div>

              {/* Número de tarjeta enmascarado */}
              <div className="text-lg font-mono mb-2">
                {maskCardNumber(card.card_number)}
              </div>

              {/* Nickname */}
              {card.nickname && (
                <div className="text-sm text-gray-600 mb-4">
                  {card.nickname}
                </div>
              )}

              {/* Saldo */}
              <div className="mb-2">
                <span className="text-sm text-gray-600">Saldo disponible:</span>
                <div className={`
                  text-2xl font-bold
                  ${isZeroBalance ? 'balance-zero text-red-600' : 'text-gray-900'}
                `}>
                  {formatBalance(card.balance)}
                </div>
                {isZeroBalance && (
                  <span className="text-xs text-red-600 font-semibold">
                    Sin fondos
                  </span>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Mensaje de límite alcanzado */}
      {hasMaxCards && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
          <p className="text-yellow-800 font-semibold">
            Has alcanzado el máximo de 3 tarjetas
          </p>
          <p className="text-yellow-700 text-sm mt-1">
            Elimina una tarjeta existente si deseas agregar otra
          </p>
        </div>
      )}

      {/* Botón agregar tarjeta (solo si < 3) */}
      {!hasMaxCards && (
        <button className="w-full md:w-auto px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
          + Agregar Tarjeta
        </button>
      )}
    </div>
  );
};
