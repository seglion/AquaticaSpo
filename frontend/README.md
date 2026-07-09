# SwellBeat Frontend (Aquatica)

This is the frontend for the Aquatica/SwellBeat application, built with Vue 3, Vite, and TypeScript.

## Getting Started (Docker)

The frontend is integrated into the main Docker Compose stack.

### 1. Start the Stack
Run this from the project root:
```bash
docker-compose up -d --build frontend
```

### 2. Access the App
Open [http://localhost:5173](http://localhost:5173) in your browser.

### 3. Development
The `frontend` directory is mounted into the container. Changes to files in `src/` will trigger Hot Module Replacement (HMR) automatically.

## Project Structure
Adheres to Atomic Design principles:
-   `src/components/atoms`: Basic UI elements.
-   `src/components/molecules`: Functional groups.
-   `src/components/organisms`: Complex blocks.
-   `src/stores`: Pinia state management.

## Testing
Run tests inside the container (or locally if Node is installed):
```bash
docker-compose exec frontend npm run test
```
