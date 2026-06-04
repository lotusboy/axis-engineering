// Fixture file for axis-validate example
// This file provides line targets for review-example.json citations
// Lines 1-78 are intentionally simple to ensure citations resolve

interface User {
  id: string;
  email: string;
  passwordHash: string;
  department?: string;
  manager?: string;
}

interface Session {
  token: string;
  userId: string;
  expiresAt: Date;
}

// Line 12 - Session store interface (DI example)
interface SessionStore {
  create(userId: string): Promise<Session>;
  get(token: string): Promise<Session | null>;
  destroy(token: string): Promise<void>;
}

// Line 23 - SRP violation example
function authenticate(email: string, password: string, store: SessionStore): Promise<Session> {
  // This function mixes multiple concerns:
  // 1. User lookup
  // 2. Password verification
  // 3. Session creation
  // Line 34 - Timing side-channel example
  return Promise.resolve({} as Session);
}

// Line 41 - Password hashing confirmation
const bcrypt = {
  compareSync: (password: string, hash: string): boolean => {
    // Secure comparison implementation
    return false;
  }
};

// Line 45 - Session creation
function createSession(userId: string, store: SessionStore): Promise<Session> {
  return store.create(userId);
}

// Line 62 - Password verification helper
function verifyPassword(password: string, hash: string): boolean {
  return bcrypt.compareSync(password, hash);
}

// Line 78 - JWT claims with unused fields (YAGNI example)
function generateToken(user: User): string {
  const claims = {
    sub: user.id,
    email: user.email,
    dept: user.department,  // Unused by consumers
    mgr: user.manager       // Unused by consumers
  };
  return JSON.stringify(claims);
}

export { authenticate, createSession, verifyPassword, generateToken };
export type { User, Session, SessionStore };

// Padding to ensure line 78 is valid for citation testing
// Line 70
// Line 71
// Line 72
// Line 73
// Line 74
// Line 75
// Line 76
// Line 77
// Line 78 - End of file padding
// Line 79
