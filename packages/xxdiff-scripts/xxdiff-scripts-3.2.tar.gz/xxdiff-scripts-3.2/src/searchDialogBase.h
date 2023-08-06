/****************************************************************************
** Form interface generated from reading ui file 'searchDialogBase.ui'
**
** Created: Tue Jan 27 16:05:18 2009
**
** WARNING! All changes made in this file will be lost!
****************************************************************************/

#ifndef XXSEARCHDIALOGBASE_H
#define XXSEARCHDIALOGBASE_H

#include <qvariant.h>
#include <qdialog.h>

class QVBoxLayout;
class QHBoxLayout;
class QGridLayout;
class QSpacerItem;
class QLabel;
class QLineEdit;
class QGroupBox;
class QCheckBox;
class QPushButton;
class QComboBox;

class XxSearchDialogBase : public QDialog
{
    Q_OBJECT

public:
    XxSearchDialogBase( QWidget* parent = 0, const char* name = 0, bool modal = FALSE, WFlags fl = 0 );
    ~XxSearchDialogBase();

    QLabel* TextLabel1;
    QLineEdit* _lineeditSearchString;
    QGroupBox* GroupBox1;
    QCheckBox* _checkboxCaseSensitive;
    QCheckBox* _checkboxUseRegexp;
    QPushButton* _buttonApply;
    QPushButton* _buttonPrevious;
    QPushButton* _buttonNext;
    QPushButton* _buttonClose;
    QLabel* TextLabel1_2;
    QLineEdit* _lineeditGotoLine;
    QComboBox* _comboGotoWhichFile;
    QPushButton* _buttonGotoLine;

protected:
    QVBoxLayout* XxSearchDialogBaseLayout;
    QHBoxLayout* Layout3;
    QHBoxLayout* GroupBox1Layout;
    QHBoxLayout* Layout5;
    QSpacerItem* Horizontal_Spacing2;
    QHBoxLayout* Layout5_2;
    QSpacerItem* Spacer2;

protected slots:
    virtual void languageChange();

};

#endif // XXSEARCHDIALOGBASE_H
