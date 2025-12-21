import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import 'package:intl/intl.dart';
import 'package:nutrition_app/main.dart';
import 'package:nutrition_app/models/food.dart';
import 'package:nutrition_app/models/log.dart';
import 'dart:developer' as developer;
// import 'package:flutter_barcode_scanner/flutter_barcode_scanner.dart';

class LogFoodScreen extends StatefulWidget {
  final int userId;
  final DailyLogModel? editLog;

  const LogFoodScreen({super.key, required this.userId, this.editLog});

  @override
  State<LogFoodScreen> createState() => _LogFoodScreenState();
}

class _LogFoodScreenState extends State<LogFoodScreen> {
  final ImagePicker _picker = ImagePicker();
  XFile? _image;

  // Controllers for manual logging
  final _foodNameController = TextEditingController();
  final _caloriesController = TextEditingController();
  final _proteinController = TextEditingController();
  final _carbsController = TextEditingController();
  final _fatsController = TextEditingController();
  final _quantityController = TextEditingController();

  // Controller and state for the search functionality
  final _searchController = TextEditingController();
  List<Food> _searchResults = [];
  bool _isLoading = false;
  bool _isSearching = false;
  Timer? _debounce;

  // Add date selection
  DateTime _selectedDate = DateTime.now();
  bool _isEditing = false;
  int? _selectedFoodId;

  @override
  void initState() {
    super.initState();
    // Add a listener to the search controller to handle debouncing
    _searchController.addListener(_onSearchChanged);

    // If editing an existing log, populate the fields
    if (widget.editLog != null) {
      _isEditing = true;
      _selectedDate = widget.editLog!.date;
      _quantityController.text = widget.editLog!.quantity.toString();

      // Pre-populate food if available
      if (widget.editLog!.food != null) {
        _foodNameController.text = widget.editLog!.food!.name;
        _caloriesController.text = widget.editLog!.food!.calories.toString();
        _proteinController.text = widget.editLog!.food!.protein.toString();
        _carbsController.text = widget.editLog!.food!.carbs.toString();
        _fatsController.text = widget.editLog!.food!.fats.toString();
      }
    }
  }

  @override
  void dispose() {
    // Cancel the timer to prevent memory leaks
    _debounce?.cancel();

    // Dispose all text editing controllers
    _foodNameController.dispose();
    _caloriesController.dispose();
    _proteinController.dispose();
    _carbsController.dispose();
    _fatsController.dispose();
    _quantityController.dispose();
    _searchController.removeListener(_onSearchChanged);
    _searchController.dispose();

    super.dispose();
  }

  void _onSearchChanged() {
    // If a debounce timer is already active, cancel it
    if (_debounce?.isActive ?? false) _debounce!.cancel();

    // Set up a new debounce timer
    _debounce = Timer(const Duration(milliseconds: 500), () {
      final query = _searchController.text;
      if (query.isNotEmpty) {
        _performSearch(query);
      } else {
        // Clear results if the search query is empty
        if (mounted) {
          setState(() {
            _searchResults = [];
            _isSearching = false;
          });
        }
      }
    });
  }

  Future<void> _performSearch(String query) async {
    if (!mounted) return;
    setState(() {
      _isSearching = true;
    });

    try {
      final results = await apiService.searchFood(query);
      if (mounted) {
        if (results.isEmpty) {
          // Fallback: check local nutrition DB (must match backend keys)
          final localDb = {
            'apple': Food(
              name: 'Apple',
              calories: 52,
              protein: 0.3,
              carbs: 14,
              fats: 0.2,
              servingSize: '1 medium apple (150g)',
            ),
            'banana': Food(
              name: 'Banana',
              calories: 89,
              protein: 1.1,
              carbs: 23,
              fats: 0.3,
              servingSize: '1 medium banana (120g)',
            ),
            'orange': Food(
              name: 'Orange',
              calories: 49,
              protein: 0.9,
              carbs: 13,
              fats: 0.1,
              servingSize: '1 medium orange (130g)',
            ),
            'chicken': Food(
              name: 'Chicken',
              calories: 165,
              protein: 31,
              carbs: 0,
              fats: 3.6,
              servingSize: '100g cooked breast',
            ),
            'beef': Food(
              name: 'Beef',
              calories: 250,
              protein: 26,
              carbs: 0,
              fats: 17,
              servingSize: '100g cooked steak',
            ),
            'rice': Food(
              name: 'Rice',
              calories: 130,
              protein: 2.7,
              carbs: 28,
              fats: 0.3,
              servingSize: '1 cup cooked (150g)',
            ),
            'bread': Food(
              name: 'Bread',
              calories: 265,
              protein: 9.4,
              carbs: 49,
              fats: 3.2,
              servingSize: '2 slices (60g)',
            ),
            'pizza': Food(
              name: 'Pizza',
              calories: 266,
              protein: 11,
              carbs: 33,
              fats: 10,
              servingSize: '1 slice (100g)',
            ),
            'pasta': Food(
              name: 'Pasta',
              calories: 157,
              protein: 5.8,
              carbs: 31,
              fats: 0.9,
              servingSize: '1 cup cooked (140g)',
            ),
            'salad': Food(
              name: 'Salad',
              calories: 25,
              protein: 1.5,
              carbs: 4.5,
              fats: 0.2,
              servingSize: '1 cup mixed greens (50g)',
            ),
            'yogurt': Food(
              name: 'Yogurt',
              calories: 61,
              protein: 3.5,
              carbs: 4.7,
              fats: 3.3,
              servingSize: '100g plain yogurt',
            ),
            'eggs': Food(
              name: 'Eggs',
              calories: 155,
              protein: 13,
              carbs: 1.1,
              fats: 11,
              servingSize: '2 large eggs (100g)',
            ),
            'fish': Food(
              name: 'Fish',
              calories: 146,
              protein: 25,
              carbs: 0,
              fats: 5.2,
              servingSize: '100g salmon',
            ),
            'potatoes': Food(
              name: 'Potatoes',
              calories: 77,
              protein: 2,
              carbs: 17,
              fats: 0.1,
              servingSize: '1 medium potato (173g)',
            ),
          };
          final key = query.toLowerCase().replaceAll(' ', '');
          if (localDb.containsKey(key)) {
            setState(() {
              _searchResults = [localDb[key]!];
            });
            _showSnackBar('Loaded from local database.');
          } else {
            setState(() {
              _searchResults = [];
            });
            _showSnackBar('No results found.');
          }
        } else {
          setState(() {
            _searchResults = results;
          });
        }
      }
    } catch (e) {
      developer.log('Error searching food: $e');
      if (mounted) {
        _showSnackBar('Failed to search food: $e');
      }
    } finally {
      if (mounted) {
        setState(() {
          _isSearching = false;
        });
      }
    }
  }

  void _populateFoodFields(Food food) {
    _foodNameController.text = food.name;
    _caloriesController.text = food.calories.toString();
    _proteinController.text = food.protein.toString();
    _carbsController.text = food.carbs.toString();
    _fatsController.text = food.fats.toString();
    _selectedFoodId = food.id;

    // Clear search results and controller after selection
    if (mounted) {
      setState(() {
        _searchResults = [];
        _searchController.text = '';
        // Hide keyboard
        FocusScope.of(context).unfocus();
      });
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      XFile? picked;

      if (source == ImageSource.gallery) {
        // Use file picker for accessing all files/folders
        FilePickerResult? result = await FilePicker.platform.pickFiles(
          type: FileType.image,
          allowMultiple: false,
          dialogTitle: 'Select Food Image',
          // Allow access to all file locations
          allowCompression: true,
          withData: false, // We don't need the data, just the path
        );

        if (result != null && result.files.isNotEmpty) {
          final file = result.files.first;
          if (file.path != null) {
            picked = XFile(file.path!);
          }
        }
      } else {
        // Use camera as before
        picked = await _picker.pickImage(
          source: source,
          imageQuality: 80,
          maxWidth: 1024,
          maxHeight: 1024,
        );
      }

      if (picked != null && mounted) {
        setState(() => _image = picked);
        _showSnackBar('Analyzing image...');

        try {
          final dynamic apiResult = await apiService.identifyFood(picked.path);

          print('🎯 API call successful, processing response...');

          // Debug: Print the API response type and content
          print('🔍 API Response Type: ${apiResult.runtimeType}');
          print(
            '🔍 API Response Keys: ${apiResult is Map ? apiResult.keys : 'Not a map'}',
          );
          print('🔍 API Response Full: $apiResult');

          // ✅ EXTRACT THE DETECTED FOOD NAME SAFELY (User's fix)
          String detectedFood = "Unknown food";

          if (apiResult is Map<String, dynamic>) {
            if (apiResult.containsKey('food_identified')) {
              detectedFood = apiResult['food_identified'];
            } else if (apiResult.containsKey('ready_to_log') &&
                apiResult['ready_to_log'] is Map<String, dynamic> &&
                apiResult['ready_to_log'].containsKey('food_name')) {
              detectedFood = apiResult['ready_to_log']['food_name'];
            }
          }

          print('🍽️ Final food detected: $detectedFood');

          // Only update search controller if we have a valid food name
          if (detectedFood != 'Unknown food') {
            setState(() {
              _searchController.text = detectedFood;
            });
          }

          // Handle our Google Vision API response format
          print(
            '🔍 Checking for ready_to_log key: ${apiResult is Map ? apiResult.containsKey('ready_to_log') : 'Not a map'}',
          );

          // ✅ SAFER PARSING (ChatGPT's fix)
          if (apiResult is Map && apiResult['ready_to_log'] != null) {
            print('✅ Found ready_to_log data!');

            final readyData = apiResult['ready_to_log'];
            final foodName =
                readyData['food_name'] ??
                apiResult['food_identified'] ??
                'Unknown food';

            print('✅ Food recognized: $foodName');

            // Direct nutrition data available - use it immediately!
            setState(() {
              _foodNameController.text =
                  readyData['food_name']?.toString() ?? foodName;
              _caloriesController.text =
                  readyData['calories']?.toString() ?? '0';
              _proteinController.text = readyData['protein']?.toString() ?? '0';
              _carbsController.text = readyData['carbs']?.toString() ?? '0';
              _fatsController.text = readyData['fats']?.toString() ?? '0';
              _quantityController.text =
                  '1.0'; // Always 1 serving, not the grams from API
              // ✅ Instead, ensure it only gets set to valid food names
              if (foodName != 'Unknown food') {
                _searchController.text = foodName;
              }
            });

            _selectedFoodId = null; // No database lookup needed

            final method = apiResult['recognition_method'] ?? 'AI Recognition';
            final confidence = apiResult['confidence'] != null
                ? '${(apiResult['confidence'] * 100).round()}%'
                : '';

            _showSnackBar('✅ $method: $foodName ($confidence)');
          } else {
            print('⚠️ No ready_to_log found, falling back to search...');

            // Fallback: Only search if we have a valid food name
            final foodName = apiResult is Map
                ? (apiResult['food_identified'] ?? detectedFood)
                : detectedFood;

            if (foodName != 'Unknown food') {
              print('🧠 Searching for recognized food: $foodName');
              _performSearch(foodName);
              _showSnackBar('🔍 Searching for: $foodName');
            } else {
              print('⚠️ AI could not identify food clearly');
              _showSnackBar('⚠️ Could not identify food. Please type the food name manually.');
            }
          }
        } catch (e, stackTrace) {
          print('❌ EXCEPTION in image processing: $e');
          print('❌ Stack trace: $stackTrace');
          developer.log(
            'Food identification error: $e',
            stackTrace: stackTrace,
          );
          _showSnackBar('Failed to identify food. Please try again.');
        }
      }
    } catch (e) {
      developer.log('Image picking error: $e');
      _showSnackBar('Failed to pick image: $e');
    }
  }

  Future<void> _openFilePicker() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.image,
        allowMultiple: false,
        dialogTitle: 'Select Food Image from Files',
        // Enable all file access for Google Files integration
        allowCompression: true,
        withData: false,
        // This allows access to Google Drive, Downloads, etc.
        initialDirectory: null, // Let system choose default
      );

      if (result != null && result.files.isNotEmpty) {
        final file = result.files.first;
        if (file.path != null) {
          // Create XFile from the selected file path
          final pickedFile = XFile(file.path!);

          // Set the image and process it
          setState(() => _image = pickedFile);
          _showSnackBar('Processing selected image...');

          try {
            final dynamic apiResult = await apiService.identifyFood(
              pickedFile.path,
            );

            // ✅ EXTRACT FOOD NAME SAFELY (Same fix as camera/gallery)
            String foodName = "Unknown food";

            if (apiResult is Map && apiResult['ready_to_log'] != null) {
              final readyData = apiResult['ready_to_log'];
              foodName =
                  readyData['food_name'] ??
                  apiResult['food_identified'] ??
                  'Unknown food';

              // ✅ AUTO-FILL FORM FIELDS
              setState(() {
                _foodNameController.text =
                    readyData['food_name']?.toString() ?? foodName;
                _caloriesController.text =
                    readyData['calories']?.toString() ?? '0';
                _proteinController.text =
                    readyData['protein']?.toString() ?? '0';
                _carbsController.text = readyData['carbs']?.toString() ?? '0';
                _fatsController.text = readyData['fats']?.toString() ?? '0';
                _quantityController.text = '1.0'; // Always 1 serving
                _searchController.text =
                    foodName; // Set search controller to recognized food
              });

              _selectedFoodId = null;

              final method =
                  apiResult['recognition_method'] ?? 'AI Recognition';
              final confidence = apiResult['confidence'] != null
                  ? '${(apiResult['confidence'] * 100).round()}%'
                  : '';

              _showSnackBar('✅ $method: $foodName ($confidence)');
            } else {
              // Fallback: Extract from other fields
              if (apiResult is String && apiResult.isNotEmpty) {
                foodName = apiResult;
              } else if (apiResult is Map<String, dynamic>) {
                foodName =
                    apiResult['food_identified'] ??
                    apiResult['food_name'] ??
                    'Unknown food';
              }

              // Only search if we have a valid food name
              if (foodName != 'Unknown food') {
                _searchController.text = foodName;
                await _performSearch(foodName);
                _showSnackBar('🔍 Searching for: $foodName');
              } else {
                _showSnackBar('⚠️ Could not identify food clearly. Please type the food name manually.');
              }
            }
          } catch (e) {
            developer.log('File identification error: $e');
            _showSnackBar('Failed to identify food. Please try again.');
          }
        }
      }
    } catch (e) {
      developer.log('File picker error: $e');
      _showSnackBar('Failed to open file picker. Please try again.');
    }
  }

  Future<void> _showImageSourceDialog() async {
    await showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Choose Image Source'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.camera_alt),
                title: const Text('Take Photo'),
                subtitle: const Text('Use camera to capture food'),
                onTap: () {
                  Navigator.of(context).pop();
                  _pickImage(ImageSource.camera);
                },
              ),
              ListTile(
                leading: const Icon(Icons.folder_open),
                title: const Text('Choose from Files'),
                subtitle: const Text('Select from any folder'),
                onTap: () {
                  Navigator.of(context).pop();
                  _openFilePicker();
                },
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
          ],
        );
      },
    );
  }

  /*
  Future<void> _scanBarcode() async {
    try {
      final String barcode = await FlutterBarcodeScanner.scanBarcode(
        '#ff6666', // color
        'Cancel', // cancel button text
        true, // show flash icon
        ScanMode.BARCODE,
      );

      if (!mounted || barcode == '-1') return;

      final product = await _openFoodFactsService.getProductByBarcode(barcode);
      
      if (product.containsKey('product')) {
        final food = Food.fromOpenFoodFacts(product['product']);
        _populateFoodFields(food);
      } else {
        _showSnackBar('Product not found for this barcode.');
      }
    } catch (e) {
      _showSnackBar('Failed to scan barcode: $e');
    }
  }
  */

  Future<void> _logFood() async {
    if (!mounted) return;
    setState(() {
      _isLoading = true;
    });

    try {
      int? foodId;
      if (_selectedFoodId != null) {
        foodId = _selectedFoodId;
        developer.log('Using existing food ID: $foodId');
      } else {
        final newFood = Food(
          name: _foodNameController.text,
          calories: double.tryParse(_caloriesController.text) ?? 0.0,
          protein: double.tryParse(_proteinController.text) ?? 0.0,
          carbs: double.tryParse(_carbsController.text) ?? 0.0,
          fats: double.tryParse(_fatsController.text) ?? 0.0,
        );
        developer.log('Creating new food: ${newFood.name}');
        final createdFood = await apiService.createFood(newFood);
        developer.log(
          'Created food response: ${createdFood.id}, ${createdFood.name}',
        );
        foodId = createdFood.id;
        if (foodId != null && foodId <= 0) {
          throw Exception('Food creation failed - invalid ID returned');
        }
      }

      final quantity = double.tryParse(_quantityController.text) ?? 1.0;
      if (_isEditing && widget.editLog != null) {
        // Update existing log
        final updateData = {
          'quantity': quantity,
          'food_id': foodId,
          'date': DateFormat('yyyy-MM-dd').format(_selectedDate),
        };

        await apiService.updateLog(widget.editLog!.id, updateData);
      } else {
        // Create new log (existing code)
        final logData = {
          'food_id': foodId,
          'quantity': quantity,
          'date': DateFormat('yyyy-MM-dd').format(_selectedDate),
          'user_id': widget.userId,
        };

        await apiService.addLog(logData);
      }

      if (mounted) {
        Navigator.of(context).pop(true); // Indicate success
      }
    } catch (e, s) {
      developer.log('Error logging food: $e');
      developer.log('Stack trace: $s');
      if (mounted) {
        _showSnackBar('Failed to log food: $e');
        Navigator.of(context).pop(false); // Indicate failure
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  void _showSnackBar(String message) {
    if (mounted) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text(message)));
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(title: const Text('Log Food')),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextField(
                controller: _searchController,
                decoration: InputDecoration(
                  labelText: 'Search Food (e.g., Apple)',
                  border: const OutlineInputBorder(),
                  suffixIcon: _isSearching
                      ? const Padding(
                          padding: EdgeInsets.all(8.0),
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.search),
                ),
              ),
              if (_searchResults.isNotEmpty)
                Container(
                  constraints: const BoxConstraints(maxHeight: 200),
                  decoration: BoxDecoration(
                    border: Border.all(color: Colors.grey.shade300),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: ListView.builder(
                    shrinkWrap: true,
                    itemCount: _searchResults.length,
                    itemBuilder: (context, index) {
                      final food = _searchResults[index];
                      return ListTile(
                        title: Text(food.name),
                        subtitle: Text('Per ${food.servingSize ?? 'N/A'}'),
                        onTap: () => _populateFoodFields(food),
                      );
                    },
                  ),
                ),
              const SizedBox(height: 16),

              // Enhanced AI Food Recognition Section (Fixed Background)
              Container(
                margin: const EdgeInsets.symmetric(vertical: 8),
                decoration: BoxDecoration(
                  // Remove gradient, use solid background to match app theme
                  color: theme.colorScheme.surface,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: theme.colorScheme.outline.withOpacity(0.3),
                    width: 1,
                  ),
                  boxShadow: [
                    BoxShadow(
                      color: theme.shadowColor.withOpacity(0.08),
                      blurRadius: 4,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Header with Icon
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: theme.colorScheme.primary,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Icon(
                              Icons.smart_toy_rounded,
                              color: theme.colorScheme.onPrimary,
                              size: 24,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  'AI Food Recognition',
                                  style: theme.textTheme.titleMedium?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: theme.colorScheme.onSurface,
                                  ),
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  'Smart identification powered by AI',
                                  style: theme.textTheme.bodySmall?.copyWith(
                                    color: theme.colorScheme.onSurfaceVariant,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: 20),

                      // Single Feature Chip (Removed unnecessary ones)
                      _buildFeatureChip(
                        theme,
                        Icons.restaurant_rounded,
                        'Nutrition Data',
                      ),

                      const SizedBox(height: 20),

                      // Action Buttons in a Grid (All Green)
                      Row(
                        children: [
                          // Camera Button (Already green)
                          Expanded(
                            child: ElevatedButton.icon(
                              style: ElevatedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(
                                  vertical: 16,
                                ),
                                backgroundColor:
                                    theme.colorScheme.primary, // Green
                                foregroundColor: theme.colorScheme.onPrimary,
                                elevation: 0,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              onPressed: () => _pickImage(ImageSource.camera),
                              icon: const Icon(Icons.camera_alt),
                              label: const Text('📷 Take Photo'),
                            ),
                          ),

                          const SizedBox(width: 12),

                          // Files Button (Now also green)
                          Expanded(
                            child: ElevatedButton.icon(
                              style: ElevatedButton.styleFrom(
                                padding: const EdgeInsets.symmetric(
                                  vertical: 16,
                                ),
                                backgroundColor: theme
                                    .colorScheme
                                    .primary, // Changed to green like camera
                                foregroundColor: theme.colorScheme.onPrimary,
                                elevation: 0,
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                              ),
                              onPressed: () => _openFilePicker(),
                              icon: const Icon(Icons.folder_open),
                              label: const Text('📁 From Files'),
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: 12),

                      // Alternative Dialog Button (Also green)
                      SizedBox(
                        width: double.infinity,
                        child: OutlinedButton.icon(
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            side: BorderSide(
                              color: theme.colorScheme.primary, // Green border
                              width: 1.5,
                            ),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                            ),
                          ),
                          onPressed: _showImageSourceDialog,
                          icon: Icon(
                            Icons.image_search_rounded,
                            color: theme.colorScheme.primary, // Green icon
                          ),
                          label: Text(
                            'More Options',
                            style: TextStyle(
                              color: theme.colorScheme.primary, // Green text
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              // Enhanced Image Preview with Better Feedback
              if (_image != null) ...[
                const SizedBox(height: 16),
                Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: theme.shadowColor.withOpacity(0.15),
                        blurRadius: 12,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(16),
                    child: Container(
                      decoration: BoxDecoration(
                        border: Border.all(
                          color: theme.colorScheme.primary.withOpacity(0.3),
                          width: 2,
                        ),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          // Image with overlay
                          Stack(
                            children: [
                              Image.file(
                                File(_image!.path),
                                height: 200,
                                width: double.infinity,
                                fit: BoxFit.cover,
                              ),
                              // Success overlay
                              Positioned.fill(
                                child: Container(
                                  decoration: BoxDecoration(
                                    gradient: LinearGradient(
                                      colors: [
                                        Colors.transparent,
                                        Colors.black.withOpacity(0.3),
                                      ],
                                      begin: Alignment.topCenter,
                                      end: Alignment.bottomCenter,
                                    ),
                                  ),
                                ),
                              ),
                              // Success indicator
                              Positioned(
                                top: 12,
                                right: 12,
                                child: Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                    vertical: 4,
                                  ),
                                  decoration: BoxDecoration(
                                    color: Colors.green.shade600,
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(
                                        Icons.check_circle_rounded,
                                        color: Colors.white,
                                        size: 16,
                                      ),
                                      const SizedBox(width: 4),
                                      Text(
                                        'Analyzed',
                                        style: theme.textTheme.bodySmall
                                            ?.copyWith(
                                              color: Colors.white,
                                              fontWeight: FontWeight.w600,
                                            ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ),

                          // Status section with clearer feedback
                          Container(
                            padding: const EdgeInsets.all(16),
                            color: theme.colorScheme.surface,
                            child: Row(
                              children: [
                                Icon(
                                  Icons.restaurant_rounded,
                                  color: theme.colorScheme.primary,
                                  size: 20,
                                ),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'AI Analysis Complete',
                                        style: theme.textTheme.bodyMedium
                                            ?.copyWith(
                                              color:
                                                  theme.colorScheme.onSurface,
                                              fontWeight: FontWeight.w600,
                                            ),
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        _selectedFoodId != null
                                            ? 'Nutrition data has been loaded into the form below'
                                            : 'Food identified - select from search results above',
                                        style: theme.textTheme.bodySmall
                                            ?.copyWith(
                                              color: theme
                                                  .colorScheme
                                                  .onSurfaceVariant,
                                            ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],

              const Divider(height: 32),

              Text('Or Log Manually', style: theme.textTheme.headlineSmall),
              const SizedBox(height: 16),

              // Manual logging fields (unchanged)
              TextField(
                controller: _foodNameController,
                decoration: const InputDecoration(
                  labelText: 'Food Name',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _caloriesController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Calories (kcal)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _proteinController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Protein (g)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _carbsController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Carbs (g)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _fatsController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Fats (g)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: _quantityController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Quantity (e.g., 1, 100)',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 24),
              _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      onPressed: _logFood,
                      child: const Text('Log Food'),
                    ),
            ],
          ),
        ),
      ),
    );
  }

  // Helper method for feature chip
  Widget _buildFeatureChip(ThemeData theme, IconData icon, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: theme.colorScheme.primary.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: theme.colorScheme.primary.withOpacity(0.2)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: theme.colorScheme.primary),
          const SizedBox(width: 6),
          Text(
            label,
            style: theme.textTheme.bodySmall?.copyWith(
              color: theme.colorScheme.primary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}
