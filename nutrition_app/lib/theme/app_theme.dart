import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // Color Palette
  static const Color background = Color(0xFF0F172A); // Deep Slate
  static const Color surface = Color(0xFF1E293B);
  static const Color primary = Color(0xFF10B981); // Neon Emerald
  static const Color primaryDark = Color(0xFF059669);
  static const Color secondary = Color(0xFF06B6D4); // Cyan
  static const Color accent = Color(0xFFF59E0B); // Amber
  static const Color error = Color(0xFFEF4444); // Red
  static const Color textPrimary = Colors.white;
  static const Color textSecondary = Color(0xFF94A3B8); // Slate 400

  // Glassmorphism effects
  static final Color glassBackground = Colors.white.withOpacity(0.05);
  static final Color glassBorder = Colors.white.withOpacity(0.1);

  // Theme Data
  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: background,
      primaryColor: primary,
      colorScheme: const ColorScheme.dark(
        primary: primary,
        secondary: secondary,
        surface: surface,
        error: error,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: textPrimary,
      ),
      useMaterial3: true,
      
      // Typography
      textTheme: TextTheme(
        displayLarge: GoogleFonts.outfit(
            color: textPrimary, fontWeight: FontWeight.bold, fontSize: 32),
        displayMedium: GoogleFonts.outfit(
            color: textPrimary, fontWeight: FontWeight.bold, fontSize: 28),
        headlineLarge: GoogleFonts.outfit(
            color: textPrimary, fontWeight: FontWeight.w700, fontSize: 24),
        headlineMedium: GoogleFonts.outfit(
            color: textPrimary, fontWeight: FontWeight.w600, fontSize: 20),
        titleLarge: GoogleFonts.outfit(
            color: textPrimary, fontWeight: FontWeight.w600, fontSize: 18),
        bodyLarge: GoogleFonts.inter(
            color: textPrimary, fontWeight: FontWeight.normal, fontSize: 16),
        bodyMedium: GoogleFonts.inter(
            color: textPrimary, fontWeight: FontWeight.normal, fontSize: 14),
        labelLarge: GoogleFonts.inter(
            color: textSecondary, fontWeight: FontWeight.w500, fontSize: 14),
      ),

      // App Bar
      appBarTheme: AppBarTheme(
        backgroundColor: background,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: GoogleFonts.outfit(
          color: textPrimary,
          fontSize: 20,
          fontWeight: FontWeight.w600,
        ),
        iconTheme: const IconThemeData(color: textPrimary),
      ),

      // Input Decoration (Text Fields)
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surface.withOpacity(0.5),
        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: glassBorder),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: BorderSide(color: glassBorder),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: primary, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(16),
          borderSide: const BorderSide(color: error),
        ),
        hintStyle: GoogleFonts.inter(color: textSecondary),
        labelStyle: GoogleFonts.inter(color: textSecondary),
      ),

      // Buttons
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primary,
          foregroundColor: Colors.white,
          elevation: 4,
          shadowColor: primary.withOpacity(0.5),
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          textStyle: GoogleFonts.outfit(
            fontWeight: FontWeight.w600,
            fontSize: 16,
          ),
        ),
      ),
      
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: primary,
          textStyle: GoogleFonts.outfit(
            fontWeight: FontWeight.w600,
            fontSize: 16,
          ),
        ),
      ),
    );
  }
}
