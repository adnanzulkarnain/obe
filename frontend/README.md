# OBE Frontend - NextJS Application

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Run development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

## Project Structure

```
frontend/
├── app/              # Next.js 14 App Router
├── components/       # React components
├── lib/             # Utilities and API client
├── public/          # Static files
└── styles/          # Global styles
```

## Features (To Be Implemented)

- [ ] Authentication pages (Login, Register)
- [ ] Dashboard for different user roles
- [ ] Kurikulum Management UI
- [ ] CPL Management UI
- [ ] Mahasiswa Management UI
- [ ] RPS Management UI
- [ ] Analytics and Reports

## Development Roadmap

### Phase 1: Setup & Authentication
- Setup Next.js project structure
- Create API client with axios
- Implement login/register pages
- Setup authentication context

### Phase 2: Core Features
- Dashboard layouts for each role
- Kurikulum CRUD operations
- CPL management interface
- Student management

### Phase 3: Advanced Features
- RPS creation and approval workflow
- Grade input interface
- Analytics dashboards
- Reports generation

## API Integration

The frontend connects to the FastAPI backend at:
- Development: http://localhost:8000
- Production: Configure via environment variables

## Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Tech Stack

- **Framework:** Next.js 14 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **State Management:** Zustand
- **Data Fetching:** TanStack Query (React Query)
- **HTTP Client:** Axios

---

**Status:** Basic Structure - Ready for Development
**Version:** 3.0.0
