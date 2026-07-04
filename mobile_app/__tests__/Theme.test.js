import { Colors } from '../src/constants/theme';

describe('Theme constants', () => {
  it('Colors has light and dark variants', () => {
    expect(Colors.light).toBeDefined();
    expect(Colors.dark).toBeDefined();
    expect(Colors.light.primary).toBe('#0052CC');
    expect(Colors.dark.primary).toBe('#3b82f6');
    expect(Colors.light.background).toBe('#ffffff');
    expect(Colors.dark.background).toBe('#111827');
  });

  it('Colors has required keys in light mode', () => {
    const keys = ['background', 'primary', 'success', 'warning', 'danger', 'text', 'border'];
    keys.forEach(k => expect(Colors.light).toHaveProperty(k));
  });

  it('Colors has required keys in dark mode', () => {
    const keys = ['background', 'primary', 'success', 'warning', 'danger', 'text', 'border'];
    keys.forEach(k => expect(Colors.dark).toHaveProperty(k));
  });
});
