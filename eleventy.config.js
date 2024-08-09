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
				: `/${type}/${item}`;
			tags.push(indexes[type]['tag'].replace('{uri}', uri));
		}
		return tags.join('\n\t');
	});

	eleventyConfig.addPassthroughCopy({ 'src/assets': '/assets' });
	// stylesheets copying handled by PostCSS plugin
	// eleventyConfig.addPassthroughCopy({ 'src/stylesheets': '/stylesheets' });
	eleventyConfig.addPassthroughCopy({ 'src/scripts': '/scripts' });

	eleventyConfig.addPlugin(postcssPlugin);

	return {
		dir: {
			input: 'src',
		},
	};
};
