export default function() {
	if (!process.env.BACKEND_URL) {
		throw new Error('Environment variable BACKEND_URL is not set.')
	}
	return {
		backendURL: process.env.BACKEND_URL,
	}
}