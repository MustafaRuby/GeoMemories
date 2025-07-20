import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { resolve } from 'path';
import { viteStaticCopy } from 'vite-plugin-static-copy';

export default defineConfig({
	plugins: [
		sveltekit(),
		viteStaticCopy({
			targets: [
				{
					src: 'node_modules/cesium/Build/Cesium/Assets/**/*',
					dest: 'Cesium/Assets'
				},
				{
					src: 'node_modules/cesium/Build/Cesium/Widgets/**/*',
					dest: 'Cesium/Widgets'
				},
				{
					src: 'node_modules/cesium/Build/Cesium/Workers/**/*',
					dest: 'Cesium/Workers'
				},
				{
					src: 'node_modules/cesium/Build/Cesium/ThirdParty/**/*',
					dest: 'Cesium/ThirdParty'
				}
			]
		})
	],
	resolve: {
		alias: {
			cesium: resolve(__dirname, 'node_modules/cesium')
		}
	},
	define: {
		CESIUM_BASE_URL: JSON.stringify('/Cesium')
	},
	server: {
		fs: {
			allow: ['.']
		},
		proxy: {
			'/api': 'http://localhost:5000'
		}
	}
});
