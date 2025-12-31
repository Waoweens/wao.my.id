export default function() {
	return {
		backendURL: process.env.BACKEND_URL || 'http://localhost:8000',
	}
}