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

    // Draw grid or background stars here if needed

    planets.forEach(planet => {
        const screenX = (planet.x * SCALE) + (WIDTH / 2);
        const screenY = (planet.y * SCALE) + (HEIGHT / 2);

        g.beginFill(0x4dabf7);
        g.drawCircle(screenX, screenY, 4);
        g.endFill();
    });
  }, [planets]);

  if (isLoading) return <Center h={HEIGHT}><Loader /></Center>;
  if (error) return <Center h={HEIGHT}><MantineText c="red">Error loading planets: {error.message}</MantineText></Center>;

  return (
    <div style={{ display: 'flex', justifyContent: 'center' }}>
        <Stage width={WIDTH} height={HEIGHT} options={{ background: '#101113' }}>
            <Container>
                 <Graphics draw={draw} />
            </Container>
        </Stage>
    </div>
  );
}
