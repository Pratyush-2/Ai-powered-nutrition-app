import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:nutrition_app/screens/login_screen.dart';
import 'package:nutrition_app/screens/main_tabs.dart';
import 'package:nutrition_app/services/api_service.dart';
import 'package:nutrition_app/services/auth_service.dart';

final ValueNotifier<ThemeMode> themeNotifier = ValueNotifier(ThemeMode.light);

final ApiService apiService = ApiService('http://10.0.2.2:8000');
final AuthService authService = AuthService();

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final token = await authService.getToken();
  runApp(NutritionApp(isLoggedIn: token != null));
}

class NutritionApp extends StatelessWidget {
  final bool isLoggedIn;
  const NutritionApp({super.key, required this.isLoggedIn});

  @override
  Widget build(BuildContext context) {
    final baseTheme = Theme.of(context);
    return ValueListenableBuilder<ThemeMode>(
      valueListenable: themeNotifier,
      builder: (context, mode, _) {
        return MaterialApp(
          title: 'Nutrition AI',
          debugShowCheckedModeBanner: false,
          theme: ThemeData(
            colorScheme: ColorScheme.fromSeed(seedColor: Colors.green),
            useMaterial3: true,
            textTheme: GoogleFonts.interTextTheme(baseTheme.textTheme),
          ),
          darkTheme: ThemeData(
            colorScheme: ColorScheme.fromSeed(
              seedColor: Colors.green,
              brightness: Brightness.dark,
            ),
            useMaterial3: true,
            textTheme: GoogleFonts.interTextTheme(
              baseTheme.textTheme.apply(
                bodyColor: Colors.white,
                displayColor: Colors.white,
              ),
            ),
          ),
          themeMode: mode,
          home: isLoggedIn ? const MainTabs() : const LoginScreen(),
        );
      },
    );
  }
}
