import { detectLanguage, needsTranslation, simpleTranslate } from './Common';

const TranslationService = {
  detectLanguage,
  needsTranslation,
  translate: simpleTranslate
};

export default TranslationService;
