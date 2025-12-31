import postcssPlugin from "@jgarber/eleventy-plugin-postcss";
import indexes from './src/_data/indexes.json' with { type: 'json' };

import 'dotenv/config';

/** @param {import('@11ty/eleventy/UserConfig').default} eleventyConfig*/
export default async function (eleventyConfig) {
	eleventyConfig.addShortcode('loadIndex', (type) => {
		let tags = [];
		for (const item of indexes[type]['list']) {
			const uri = item.startsWith('ROOT/')
				? item.slice(4)
				: `/${type}/${item}`;
			tags.push(indexes[type]['tag'].replace('{uri}', uri));
		}
		return tags.join('\n\t');
	});

	eleventyConfig.setServerOptions({
		host: "0.0.0.0"
	})

	eleventyConfig.addPassthroughCopy({ 'src/assets': '/assets' });
	// stylesheets copying handled by PostCSS plugin
	// eleventyConfig.addPassthroughCopy({ 'src/stylesheets': '/stylesheets' });
	eleventyConfig.addPassthroughCopy({ 'src/scripts': '/scripts' });

	eleventyConfig.addPlugin(postcssPlugin);

};

export const config = {
	dir: {
		input: 'src',
		includes: '_includes',
	}
}