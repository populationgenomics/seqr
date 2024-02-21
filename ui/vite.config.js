import { defineConfig } from 'vite'
import { createHtmlPlugin } from 'vite-plugin-html'
import react from '@vitejs/plugin-react'
import svgr from 'vite-plugin-svgr'
const path = require('node:path'); 

const aliases = {
    'pages': './pages',
    'shared': './shared',
    'store': './store',
}

const resolvedAliases = Object.fromEntries(
    Object.entries(aliases).map(([key, value]) => [key, path.resolve(__dirname, value)]),
);

export default defineConfig({
    root: '.',
    build: {
        // Relative to the root
        outDir: './dist',
        emptyOutDir: true,
    },
    publicDir: 'static',
    server: {
        proxy: {
            
        },
    },
    plugins: [
        createHtmlPlugin({
            inject: {
                NODE_ENV: 'production'
            },
        }),
        react({
            // Use React plugin in all *.jsx and *.tsx files
            include: '**/*.{jsx,tsx}',
        }),
        svgr(),
    ],
    resolve: {
        alias: {
            ...resolvedAliases,
        },
    },
})
