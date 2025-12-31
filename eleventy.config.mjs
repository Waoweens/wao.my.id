import postcssPlugin from "@jgarber/eleventy-plugin-postcss";
import syntaxHighlight from "@11ty/eleventy-plugin-syntaxhighlight";
import indexes from './src/_data/indexes.json' with { type: 'json' };
import { createHash } from 'node:crypto';

import 'dotenv/config';

/** @param {import('@11ty/eleventy/UserConfig').default} eleventyConfig*/
export default async function (eleventyConfig) {
	eleventyConfig.addPlugin(postcssPlugin);
	eleventyConfig.addPlugin(syntaxHighlight, {
		codeAttributes: {
			id: ({ _, content }) => {
				return 'codeblock-' + createHash('sha1').update(content).digest('hex').slice(0, 8)
			}
		}
	});

	eleventyConfig.addPairedNunjucksShortcode('codeblock', function(content, language = 'Plain Text') {
		const id = 'codeblock-' + createHash('sha1').update(content).digest('hex').slice(0, 8)
		return this.env.render('src/_includes/components/codeblock.njk', { content, language, id });
	})

	eleventyConfig.setServerOptions({
		host: "0.0.0.0"
	})

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

	eleventyConfig.addPassthroughCopy({ 'src/assets': '/assets' });
	// stylesheets copying handled by PostCSS plugin
	// eleventyConfig.addPassthroughCopy({ 'src/stylesheets': '/stylesheets' });
	eleventyConfig.addPassthroughCopy({ 'src/scripts': '/scripts' });

};

export const config = {
	dir: {
		input: 'src',
		includes: '_includes',
	}
}