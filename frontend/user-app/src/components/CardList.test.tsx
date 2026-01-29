/**
 * Unit Tests for CardList Component
 * Tests siguiendo TDD: Red → Green → Refactor
 * 
 * TASK-041 a TASK-050: Tests para componente CardList de React
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { CardList } from './CardList';

// Mock de datos
const mockCardsData = {
  cards: [
    {
      id: 'card_001',
      card_number: '3456',
      card_type: 'DEBIT',
      balance: '1500.00',
      status: 'ACTIVE',
      nickname: 'Mi Débito Principal',
      created_at: '2026-01-28T10:00:00'
    },
    {
      id: 'card_002',
      card_number: '9876',
      card_type: 'CREDIT',
      balance: '5000.00',
      status: 'ACTIVE',
      nickname: 'Tarjeta Platinum',
      created_at: '2026-01-27T15:30:00'
    },
    {
      id: 'card_003',
      card_number: '2222',
      card_type: 'DEBIT',
      balance: '0.00',
      status: 'BLOCKED',
      nickname: 'Ahorros',
      created_at: '2026-01-26T08:00:00'
    }
  ]
};

describe('CardList Component', () => {
  beforeEach(() => {
    // Reset mocks antes de cada test
    vi.clearAllMocks();
  });

  describe('TASK-042: Rendering con datos', () => {
    it('debe renderizar 3 tarjetas cuando hay datos', async () => {
      // Given: Un usuario con 3 tarjetas
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockCardsData
      });

      // When: Se renderiza el componente
      render(<CardList />);

      // Then: Debe mostrar 3 tarjetas
      await waitFor(() => {
        const cards = screen.getAllByTestId('card-item');
        expect(cards).toHaveLength(3);
      });
    });

    it('debe mostrar los últimos 4 dígitos enmascarados', async () => {
      // Given: Tarjetas con números
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockCardsData
      });

      // When: Se renderiza
      render(<CardList />);

      // Then: Debe mostrar **** + últimos 4 dígitos
      await waitFor(() => {
        expect(screen.getByText(/\*\*\*\*3456/)).toBeInTheDocument();
        expect(screen.getByText(/\*\*\*\*9876/)).toBeInTheDocument();
        expect(screen.getByText(/\*\*\*\*2222/)).toBeInTheDocument();
      });
    });

    it('debe mostrar el saldo con formato de moneda', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockCardsData
      });

      render(<CardList />);

      await waitFor(() => {
        expect(screen.getByText(/\$1,500\.00/)).toBeInTheDocument();
        expect(screen.getByText(/\$5,000\.00/)).toBeInTheDocument();
      });
    });

    it('debe mostrar el nickname de cada tarjeta', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockCardsData
      });

      render(<CardList />);

      await waitFor(() => {
        expect(screen.getByText('Mi Débito Principal')).toBeInTheDocument();
        expect(screen.getByText('Tarjeta Platinum')).toBeInTheDocument();
        expect(screen.getByText('Ahorros')).toBeInTheDocument();
      });
    });
  });

  describe('TASK-043: Íconos y visualización por tipo', () => {
    it('debe mostrar ícono de débito para tarjetas DEBIT', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockCardsData
      });

      render(<CardList />);

      await waitFor(() => {
        const debitIcons = screen.getAllByTestId('debit-icon');
        expect(debitIcons).toHaveLength(2); // card_001 y card_003
      });
    });

    it('debe mostrar ícono de crédito para tarjetas CREDIT', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockCardsData
      });

      render(<CardList />);

      await waitFor(() => {
        const creditIcons = screen.getAllByTestId('credit-icon');
        expect(creditIcons).toHaveLength(1); // card_002
      });
    });
  });

  describe('TASK-044: Colores por estado', () => {
    it('debe aplicar estilo verde para tarjetas ACTIVE', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockCardsData
      });

      render(<CardList />);

      await waitFor(() => {
        const activeCards = screen.getAllByTestId(/card-item/);
        const activeCard = activeCards.find(card => 
          card.textContent?.includes('Mi Débito Principal')
        );
        expect(activeCard.className).toMatch('status-active');
      });
    });

    it('debe aplicar estilo rojo para tarjetas BLOCKED', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockCardsData
      });

      render(<CardList />);

      await waitFor(() => {
        const cards = screen.getAllByTestId('card-item');
        const blockedCard = cards.find(card => 
          card.textContent?.includes('Ahorros')
        );
        expect(blockedCard.className).toMatch('status-blocked');
      });
    });

    it('debe mostrar saldo en rojo cuando es $0.00', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockCardsData
      });

      render(<CardList />);

      await waitFor(() => {
        const zeroBalance = screen.getByText(/\$0\.00/);
        expect(zeroBalance.className).toMatch('balance-zero');
      });
    });

    it('debe mostrar etiqueta "Sin fondos" para saldo cero', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockCardsData
      });

      render(<CardList />);

      await waitFor(() => {
        expect(screen.getByText('Sin fondos')).toBeInTheDocument();
      });
    });
  });

  describe('TASK-045: Estado vacío', () => {
    it('debe mostrar mensaje cuando no hay tarjetas', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ cards: [] })
      });

      render(<CardList />);

      await waitFor(() => {
        expect(screen.getByText('No tienes tarjetas registradas')).toBeInTheDocument();
        expect(screen.getByText(/Agrega tu primera tarjeta/)).toBeInTheDocument();
      });
    });

    it('debe mostrar botón "Agregar Primera Tarjeta" cuando está vacío', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ cards: [] })
      });

      render(<CardList />);

      await waitFor(() => {
        const button = screen.getByRole('button', { name: /Agregar Primera Tarjeta/i });
        expect(button).toBeTruthy();
      });
    });
  });

  describe('TASK-046: Estado de carga', () => {
    it('debe mostrar loading spinner mientras carga', async () => {
      global.fetch = vi.fn().mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          ok: true,
          json: async () => mockCardsData
        }), 100))
      );

      render(<CardList />);

      // Debe mostrar loading inmediatamente
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();

      // Después de cargar, loading desaparece
      await waitFor(() => {
        expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
      });
    });
  });

  describe('TASK-047: Manejo de errores', () => {
    it('debe mostrar mensaje de error si falla la carga', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      render(<CardList />);

      await waitFor(() => {
        expect(screen.getByText(/Error al cargar tarjetas/i)).toBeInTheDocument();
      });
    });

    it('debe mostrar botón de reintentar cuando hay error', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      render(<CardList />);

      await waitFor(() => {
        const retryButton = screen.getByRole('button', { name: /Reintentar/i });
        expect(retryButton).toBeTruthy();
      });
    });
  });

  describe('TASK-048: Límite de 3 tarjetas', () => {
    it('NO debe mostrar botón "Agregar Tarjeta" cuando hay 3 tarjetas', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockCardsData // 3 tarjetas
      });

      render(<CardList />);

      await waitFor(() => {
        const addButton = screen.queryByRole('button', { name: /Agregar Tarjeta/i });
        expect(addButton).not.toBeInTheDocument();
      });
    });

    it('debe mostrar mensaje "Has alcanzado el máximo de 3 tarjetas"', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockCardsData
      });

      render(<CardList />);

      await waitFor(() => {
        expect(screen.getByText(/Has alcanzado el máximo de 3 tarjetas/i)).toBeInTheDocument();
      });
    });
  });

  describe('TASK-049: Ordenamiento', () => {
    it('debe mostrar tarjetas ordenadas por más nueva primero', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockCardsData
      });

      render(<CardList />);

      await waitFor(() => {
        const cards = screen.getAllByTestId('card-item');
        // Primera tarjeta debe ser card_001 (2026-01-28)
        expect(cards[0]).toHaveTextContent('Mi Débito Principal');
        // Última tarjeta debe ser card_003 (2026-01-26)
        expect(cards[2]).toHaveTextContent('Ahorros');
      });
    });
  });

  describe('TASK-050: Responsive', () => {
    it('debe aplicar clase grid en desktop', async () => {
      global.fetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => mockCardsData
      });

      render(<CardList />);

      await waitFor(() => {
        const container = screen.getByTestId('cards-container');
        expect(container.className).toMatch('grid');
      });
    });
  });
});
