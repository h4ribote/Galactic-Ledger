import { Stage, Graphics, Container } from '@pixi/react';
import { useQuery } from '@tanstack/react-query';
import { fetchPlanets } from '../../api/planets';
import { Center, Loader, Text as MantineText } from '@mantine/core';
import * as PIXI from 'pixi.js';
import { useCallback } from 'react';

const WIDTH = 1000;
const HEIGHT = 800;
const SCALE = 0.0004; // Map -1,000,000~1,000,000 to fit in view

export function GalaxyMap() {
  const { data: planets, isLoading, error } = useQuery({
    queryKey: ['planets'],
    queryFn: fetchPlanets,
  });

  const draw = useCallback((g: PIXI.Graphics) => {
    g.clear();

    if (!planets) return;

    // Draw Grid
    g.lineStyle(1, 0x252a3b, 0.3); // faint blue-grey
    const gridSize = 100;
    for (let x = 0; x <= WIDTH; x += gridSize) {
        g.moveTo(x, 0);
        g.lineTo(x, HEIGHT);
    }
    for (let y = 0; y <= HEIGHT; y += gridSize) {
        g.moveTo(0, y);
        g.lineTo(WIDTH, y);
    }

    // Draw Planets
    g.lineStyle(0);
    planets.forEach(planet => {
        const screenX = (planet.x * SCALE) + (WIDTH / 2);
        const screenY = (planet.y * SCALE) + (HEIGHT / 2);

        // Outer Glow
        g.beginFill(0x00f2ff, 0.2);
        g.drawCircle(screenX, screenY, 8);
        g.endFill();

        // Inner Glow
        g.beginFill(0x00f2ff, 0.6);
        g.drawCircle(screenX, screenY, 4);
        g.endFill();

        // Core
        g.beginFill(0xffffff);
        g.drawCircle(screenX, screenY, 2);
        g.endFill();
    });
  }, [planets]);

  if (isLoading) return <Center h={HEIGHT}><Loader color="brand" /></Center>;
  if (error) return <Center h={HEIGHT}><MantineText c="red">Error loading planets: {error.message}</MantineText></Center>;

  return (
    <div style={{ display: 'flex', justifyContent: 'center' }}>
        <Stage width={WIDTH} height={HEIGHT} options={{ background: '#0b0d14' }}>
            <Container>
                 <Graphics draw={draw} />
            </Container>
        </Stage>
    </div>
  );
}
