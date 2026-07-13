import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import OpsConsole from '../OpsConsole';
import { API_BASE_URL } from '../../config';

global.fetch = vi.fn();

describe('OpsConsole Component', () => {
  it('renders the telemetry stream and copilot panel', () => {
    render(<OpsConsole logs={[]} onActionExecuted={vi.fn()} />);
    expect(screen.getByText('Live Telemetry Stream')).toBeDefined();
    expect(screen.getByText('Operations Copilot (GenAI Agent)')).toBeDefined();
  });

  it('renders logs correctly', () => {
    const mockLogs = [
      { time: '12:00', type: 'system', message: 'Test log 1' },
      { time: '12:01', type: 'cctv', message: 'Test log 2' }
    ];
    render(<OpsConsole logs={mockLogs} onActionExecuted={vi.fn()} />);
    expect(screen.getByText('Test log 1')).toBeDefined();
    expect(screen.getByText('Test log 2')).toBeDefined();
  });

  it('handles copilot queries correctly', async () => {
    fetch.mockResolvedValueOnce({
      json: async () => ({
        summary: 'Operations running smoothly.',
        confidence_score: 98,
        departments: ['Security'],
        recommended_actions: []
      })
    });

    render(<OpsConsole logs={[]} onActionExecuted={vi.fn()} />);
    
    const input = screen.getByLabelText('Ask Operations Copilot Query');
    fireEvent.change(input, { target: { value: 'status' } });
    
    const button = screen.getByLabelText('Send Query');
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(screen.getByText('Operations running smoothly.')).toBeDefined();
    });
  });
});
