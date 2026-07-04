const FESTIVALS = [
  { date: { month: 1, day: 1 }, name: 'New Year', icon: 'party-popper', colors: ['#FF6B35', '#004E89'], message: 'Happy New Year!' },
  { date: { month: 1, day: 14 }, name: 'Pongal', icon: 'rice', colors: ['#C0392B', '#F39C12'], message: 'Happy Pongal!' },
  { date: { month: 1, day: 26 }, name: 'Republic Day', icon: 'flag', colors: ['#FF9933', '#138808'], message: 'Happy Republic Day!' },
  { date: { month: 4, day: 14 }, name: 'Vishu', icon: 'flower', colors: ['#FFD700', '#228B22'], message: 'Happy Vishu!' },
  { date: { month: 6, day: 29 }, name: 'Onam', icon: 'flower-lotus', colors: ['#FFD700', '#006400'], message: 'Happy Onam!' },
  { date: { month: 8, day: 15 }, name: 'Independence Day', icon: 'flag', colors: ['#FF9933', '#138808'], message: 'Happy Independence Day!' },
  { date: { month: 10, day: 2 }, name: 'Gandhi Jayanti', icon: 'meditation', colors: ['#964B00', '#F5F5DC'], message: 'Happy Gandhi Jayanti!' },
  { date: { month: 11, day: 1 }, name: 'Kerala Piravi', icon: 'map', colors: ['#008000', '#FFD700'], message: 'Happy Kerala Piravi!' },
  { date: { month: 12, day: 25 }, name: 'Christmas', icon: 'pine-tree', colors: ['#D42426', '#228B22'], message: 'Merry Christmas!' },
];

export function getActiveFestival() {
  const now = new Date();
  const month = now.getMonth() + 1;
  const day = now.getDate();

  for (const f of FESTIVALS) {
    if (f.date.month === month && f.date.day === day) {
      return f;
    }
  }
  return null;
}

export function withFestival(festival, { style, colors: overrideColors }) {
  if (!festival) return null;
  return festival;
}
