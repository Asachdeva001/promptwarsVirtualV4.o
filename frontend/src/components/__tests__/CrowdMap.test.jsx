import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import CrowdMap from '../CrowdMap';

describe('CrowdMap Component', () => {
  const mockGates = [
    { id: 'gate_a', name: 'Gate A', estimated_wait_time: 5, coordinates: { x: 10, y: 10 } },
    { id: 'gate_b', name: 'Gate B', estimated_wait_time: 25, coordinates: { x: 50, y: 50 } }
  ];

  it('renders the title correctly', () => {
    render(<CrowdMap timeline={0} setTimeline={vi.fn()} gates={mockGates} alerts={[]} onRerouteSuccess={vi.fn()} />);
    expect(screen.getByText('Predictive Crowd Intelligence Map')).toBeDefined();
  });

  it('renders gates with their wait times', () => {
    render(<CrowdMap timeline={0} setTimeline={vi.fn()} gates={mockGates} alerts={[]} onRerouteSuccess={vi.fn()} />);
    expect(screen.getByText('GATE A (5m)')).toBeDefined();
    expect(screen.getByText('GATE B (25m)')).toBeDefined();
  });

  it('handles timeline changes', () => {
    const setTimelineMock = vi.fn();
    render(<CrowdMap timeline={0} setTimeline={setTimelineMock} gates={mockGates} alerts={[]} onRerouteSuccess={vi.fn()} />);
    
    const slider = screen.getByLabelText('Crowd Prediction Timeline');
    fireEvent.change(slider, { target: { value: 20 } });
    
    expect(setTimelineMock).toHaveBeenCalledWith(20);
  });
});
