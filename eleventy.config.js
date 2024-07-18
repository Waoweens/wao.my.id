const postcssPlugin = require('@jgarber/eleventy-plugin-postcss');

/** @param {import("@11ty/eleventy").UserConfig} eleventyConfig */
module.exports = function (eleventyConfig) {
	eleventyConfig.addPassthroughCopy({ 'src/assets': '/assets' });
	// eleventyConfig.addPassthroughCopy({ 'src/_includes/styles': '/styles' });
	eleventyConfig.addPassthroughCopy({ 'src/_includes/scripts': '/scripts' });

	eleventyConfig.addPlugin(postcssPlugin);
	
	return {
		dir: {
			input: 'src',
		},
	};
};
