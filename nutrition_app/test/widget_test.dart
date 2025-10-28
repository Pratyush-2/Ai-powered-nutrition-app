import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:nutrition_app/screens/main_tabs.dart';
import 'package:shared_preferences/shared_preferences.dart';

// Mock SharedPreferences
class MockSharedPreferences extends Mock implements SharedPreferences {}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() async {
    // Set up mock shared preferences
    SharedPreferences.setMockInitialValues({
      'user_id': 1,
      'token': 'test-token',
    });
  });

  testWidgets('MainTabs has a BottomNavigationBar with 5 items', (
    WidgetTester tester,
  ) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(MaterialApp(home: MainTabs(userId: 1)));

    // Wait for any animations to complete
    await tester.pumpAndSettle();

    // Find the BottomNavigationBar
    final bottomNavBar = find.byType(BottomNavigationBar);
    expect(bottomNavBar, findsOneWidget);

    // Check for 5 items
    expect(find.byIcon(Icons.home), findsOneWidget);
    expect(find.byIcon(Icons.history), findsOneWidget);
    expect(find.byIcon(Icons.chat_bubble_outline), findsOneWidget);
    expect(find.byIcon(Icons.flag), findsOneWidget);
    expect(find.byIcon(Icons.person), findsOneWidget);
  });

  testWidgets('MainTabs handles navigation correctly', (
    WidgetTester tester,
  ) async {
    await tester.pumpWidget(MaterialApp(home: MainTabs(userId: 1)));

    // Wait for any animations
    await tester.pumpAndSettle();

    // Test navigation
    for (int i = 0; i < 5; i++) {
      await tester.tap(find.byType(BottomNavigationBar).first);
      await tester.pumpAndSettle();
    }
  });
}
