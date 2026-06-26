import { NextRequest, NextResponse } from 'next/server'

// Routes that require authentication
const AUTH_REQUIRED = ['/saved', '/history'] // Temporarily removed '/profile' for testing

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Check if route needs auth
  const needsAuth = AUTH_REQUIRED.some(route => pathname.startsWith(route))

  if (needsAuth) {
    const token = request.cookies.get('access_token')?.value
    if (!token) {
      // Redirect to login, preserving intended destination
      const loginUrl = new URL('/login', request.url)
      loginUrl.searchParams.set('redirect', pathname)
      return NextResponse.redirect(loginUrl)
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/saved/:path*', '/history/:path*', '/profile/:path*'],
}
