import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:nutrition_app/screens/login_screen.dart';
import 'package:nutrition_app/screens/main_tabs.dart';
import 'package:nutrition_app/services/api_service.dart';
import 'package:nutrition_app/services/auth_service.dart';
import 'package:nutrition_app/theme/app_theme.dart';

final ValueNotifier<ThemeMode> themeNotifier = ValueNotifier(ThemeMode.light);

final ApiService apiService = ApiService('https://ai-powered-nutrition-app.onrender.com');
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
          theme: AppTheme.darkTheme,
          darkTheme: AppTheme.darkTheme,
          themeMode: ThemeMode.dark,
          home: isLoggedIn ? const MainTabs() : const LoginScreen(),
        );
      },
    );
  }
}
