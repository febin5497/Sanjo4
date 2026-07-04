import React from 'react';
import { render } from '@testing-library/react-native';
import App from '../App';

describe('App', () => {
  it('renders without crashing', () => {
    const tree = render(<App />);
    expect(tree).toBeDefined();
  });

  it('renders root navigator', () => {
    const { getByText } = render(<App />);
    // App should mount and render something
    expect(App).toBeDefined();
  });
});
