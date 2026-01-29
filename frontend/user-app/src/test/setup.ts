// @ts-nocheck - Archivo de configuración de tests, dependencias instaladas en runtime
import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
// import * as matchers from '@testing-library/jest-dom/matchers';

// Declarar globals de vitest
declare global {
  var beforeAll: (fn: () => void) => void;
  var afterAll: (fn: () => void) => void;
}

// Extender matchers de testing-library
// expect.extend(matchers);

// Limpiar después de cada test
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

// Mock de localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
globalThis.localStorage = localStorageMock as any;

// Mock de fetch
globalThis.fetch = vi.fn();

// Mock de console.error para tests más limpios
const originalError = console.error;
beforeAll(() => {
  console.error = vi.fn();
});

afterAll(() => {
  console.error = originalError;
});
