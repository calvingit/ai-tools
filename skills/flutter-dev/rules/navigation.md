# Navigation Rules (GoRouter)

### Core Principles
1. Use **GoRouter** for all navigation requirements in Flutter applications.
2. Adopt a **declarative** routing approach where the UI reflects the current route state.
3. Centralize route definitions in a dedicated router configuration file (e.g., `app_router.dart`).
4. Avoid using `Navigator.of(context)` directly unless handling simple dialogs or bottom sheets.
5. Use `context.go()` for switching screens (replacing the stack) and `context.push()` for stacking screens (preserving history).

### Setup & Configuration
1. Define a top-level or static `GoRouter` configuration.
2. Use `MaterialApp.router` or `CupertinoApp.router` in your `main.dart`.
3. Set the `initialLocation` to your app's entry point (e.g., `/` or `/home`).
4. Define routes using `GoRoute` objects with unique `path` and `name` properties.
5. Use `builder` to return the widget for a specific route.

```dart
final router = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const HomeScreen(),
    ),
  ],
);
```

### Navigation Actions
1. Prefer **named routes** for navigation to avoid hardcoding paths.
   - Use: `context.goNamed('profile')`
   - Avoid: `context.go('/profile')` (unless simple)
2. Use `context.pop()` to return to the previous screen.
3. Use `context.replace()` to replace the current route without animating.

### Parameter Handling
1. **Path Parameters**: Use `:paramName` in the route path for required parameters.
   - Definition: `path: '/user/:id'`
   - Access: `state.pathParameters['id']`
2. **Query Parameters**: Use `?key=value` for optional parameters.
   - Access: `state.uri.queryParameters['filter']`
3. **Extra Object**: Use `extra` for passing complex objects (non-primitive).
   - Sending: `context.goNamed('details', extra: userObject)`
   - Access: `state.extra as User`
   - **Warning**: `extra` data is not persisted on web refresh; handle nulls gracefully.

### Redirection & Guards
1. Use `redirect` to protect routes (e.g., authentication checks).
2. Implement redirection logic at the top-level `GoRouter` or individual `GoRoute`.
3. Return `null` to allow navigation, or a path string to redirect.
4. Combine with a `Listenable` (like a specific auth provider) in `refreshListenable` to trigger redirects automatically on state changes.

```dart
redirect: (context, state) {
  final isLoggedIn = authService.isLoggedIn;
  final isLoggingIn = state.uri.toString() == '/login';

  if (!isLoggedIn && !isLoggingIn) return '/login';
  if (isLoggedIn && isLoggingIn) return '/';
  return null;
},
```

### Nested Navigation
1. Use `ShellRoute` or `StatefulShellRoute` for persistent bottom navigation bars or side menus.
2. `ShellRoute` rebuilds the shell when switching branches.
3. `StatefulShellRoute` preserves the state of each branch (recommended for bottom tabs).

### Error Handling
1. Provide an `errorBuilder` to show a custom 404/Error page when a route is not found.

### Type Safety
1. Consider using packages like `go_router_builder` for type-safe routes if the project scale justifies the extra code generation setup.
