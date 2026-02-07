import { createTheme } from '@mantine/core';
import type { MantineColorsTuple, MantineTheme } from '@mantine/core';

const brand: MantineColorsTuple = [
  '#e0fbff',
  '#cbf7ff',
  '#9aefff',
  '#64e7ff',
  '#3de0fe',
  '#25dbfe',
  '#09d9ff',
  '#00c0e4',
  '#00abcc',
  '#0094b4',
];

const spaceDark: MantineColorsTuple = [
    '#C1C2C5',
    '#A6A7AB',
    '#909296',
    '#5c5f66',
    '#252a3b',
    '#1a1d29',
    '#13161f',
    '#0b0d14',
    '#07080c',
    '#030406',
];

export const theme = createTheme({
  primaryColor: 'brand',
  colors: {
    brand,
    dark: spaceDark,
  },
  fontFamily: 'Inter, sans-serif',
  fontFamilyMonospace: 'JetBrains Mono, monospace',
  headings: {
    fontFamily: 'Rajdhani, sans-serif',
    fontWeight: '600',
  },
  defaultRadius: 0,
  cursorType: 'pointer',

  components: {
    Button: {
      defaultProps: {
        variant: 'outline',
        radius: 0,
      },
      styles: {
        root: {
          fontFamily: 'Rajdhani, sans-serif',
          fontWeight: 'bold',
          letterSpacing: '1px',
          textTransform: 'uppercase',
          borderWidth: '1px',
          transition: 'all 0.2s ease',
        },
      },
    },
    Paper: {
        defaultProps: {
            radius: 0,
            withBorder: true,
        },
        styles: (_theme: MantineTheme) => ({
            root: {
                backgroundColor: 'rgba(19, 22, 31, 0.85)',
                backdropFilter: 'blur(8px)',
                borderColor: 'rgba(100, 231, 255, 0.2)',
            }
        })
    },
    Card: {
        defaultProps: {
            radius: 0,
            withBorder: true,
        },
        styles: (_theme: MantineTheme) => ({
            root: {
                backgroundColor: 'rgba(19, 22, 31, 0.85)',
                backdropFilter: 'blur(8px)',
                borderColor: 'rgba(100, 231, 255, 0.2)',
            }
        })
    },
    Table: {
        styles: (theme: MantineTheme) => ({
            th: {
                fontFamily: 'Rajdhani, sans-serif',
                textTransform: 'uppercase',
                letterSpacing: '1px',
                color: theme.colors.brand[4],
                backgroundColor: 'transparent',
                borderBottom: `1px solid ${theme.colors.brand[8]}`,
            },
            td: {
                fontFamily: 'JetBrains Mono, monospace',
                fontSize: '0.9rem',
                borderBottom: `1px solid ${theme.colors.dark[4]}`,
            },
            tr: {
                '&:hover': {
                    backgroundColor: 'rgba(0, 242, 255, 0.05) !important',
                }
            }
        })
    },
    Modal: {
        styles: (theme: MantineTheme) => ({
            header: {
                backgroundColor: theme.colors.dark[6],
                fontFamily: 'Rajdhani, sans-serif',
                textTransform: 'uppercase',
            },
            content: {
                backgroundColor: theme.colors.dark[7],
                border: `1px solid ${theme.colors.brand[6]}`,
            }
        })
    },
    TextInput: {
        styles: (theme: MantineTheme) => ({
            input: {
                backgroundColor: 'rgba(0, 0, 0, 0.3)',
                borderColor: theme.colors.dark[4],
                color: theme.colors.brand[1],
                fontFamily: 'JetBrains Mono, monospace',
                '&:focus': {
                    borderColor: theme.colors.brand[5],
                }
            },
            label: {
                fontFamily: 'Rajdhani, sans-serif',
                textTransform: 'uppercase',
                fontSize: '0.8rem',
                letterSpacing: '0.5px',
                marginBottom: '4px',
            }
        })
    },
    AppShell: {
        styles: (theme: MantineTheme) => ({
            header: {
                backgroundColor: 'rgba(11, 13, 20, 0.95)',
                borderBottom: `1px solid ${theme.colors.dark[4]}`,
            },
            navbar: {
                backgroundColor: 'rgba(11, 13, 20, 0.95)',
                borderRight: `1px solid ${theme.colors.dark[4]}`,
            },
            main: {
                backgroundColor: theme.colors.dark[7],
            }
        })
    }
  },
});
