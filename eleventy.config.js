const postcssPlugin = require('@jgarber/eleventy-plugin-postcss');
const indexes = require('./src/_data/indexes.json');

/** @param {import("@11ty/eleventy").UserConfig} eleventyConfig */
module.exports = function (eleventyConfig) {
	eleventyConfig.addShortcode('loadIndex', (type) => {
		console.log(indexes);
		let tags = [];
		for (const item of indexes[type]['list']) {
			const uri = item.startsWith('ROOT/')
				? item.slice(4)
				: `/assets/${type}/${item}`;
			tags.push(indexes[type]['tag'].replace('{uri}', uri));
		}
		return tags.join('\t\n');
	});

	eleventyConfig.addPassthroughCopy({ 'src/assets': '/assets' });
	eleventyConfig.addPassthroughCopy({
		'src/_includes/stylesheets': '/assets/stylesheets',
	});
	eleventyConfig.addPassthroughCopy({
		'src/_includes/scripts': '/assets/scripts',
	});

	eleventyConfig.addPlugin(postcssPlugin);

	return {
		dir: {
			input: 'src',
		},
	};
};
