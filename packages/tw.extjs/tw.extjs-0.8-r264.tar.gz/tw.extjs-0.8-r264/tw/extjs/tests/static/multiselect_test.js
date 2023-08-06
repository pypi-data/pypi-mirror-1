
function setUp() {

    panelItem = {
            xtype:"itemselector",
            name:"itemselector",
            fieldLabel:"States",
            dataFields:['code', 'desc'],
            fromData:[['AL', 'Alabama'], ['AK', 'Alaska'], ['AZ', 'Arizona'], ['AR', 'Arkansas'], ['CA', 'California'], ['CO', 'Colorado'], ['CT', 'Connecticut'], ['DE', 'Delaware'], ['FL', 'Florida'], ['GA', 'Georgia'], ['HI', 'Hawaii'], ['ID', 'Idaho'], ['IL', 'Illinois'], ['IN', 'Indiana'], ['IA', 'Iowa'], ['KS', 'Kansas'], ['KY', 'Kentucky'], ['LA', 'Louisiana'], ['ME', 'Maine'], ['MD', 'Maryland'], ['MA', 'Massachusetts'], ['MI', 'Michigan'], ['MN', 'Minnesota'], ['MS', 'Mississippi'], ['MO', 'Missouri'], ['MT', 'Montana'], ['NE', 'Nebraska'], ['NV', 'Nevada'], ['NH', 'New Hampshire'], ['NJ', 'New Jersey'], ['NM', 'New Mexico'], ['NY', 'New York'], ['NC', 'North Carolina'], ['ND', 'North Dakota'], ['OH', 'Ohio'], ['OK', 'Oklahoma'], ['OR', 'Oregon'], ['PA', 'Pennsylvania'], ['RI', 'Rhode Island'], ['SC', 'South Carolina'], ['SD', 'South Dakota'], ['TN', 'Tennessee'], ['TX', 'Texas'], ['UT', 'Utah'], ['VT', 'Vermont'], ['VA', 'Virginia'], ['WA', 'Washington'], ['WV', 'West Virginia'], ['WI', 'Wisconsin'], ['WY', 'Wyoming']],
            toData:[],
            msWidth:200,
            msHeight:200,
            valueField:"code",
            displayField:"desc",
            toLegend:"Selected",
            fromLegend:"Available",
            TBar:[{
                text:"Clear",
                handler:function(){
                    var i=formItemSelector.getForm().findField("itemselector");
                    i.reset.call(i);
                }
            }]

    }

buttonSave = {
            text: "Save",
            handler: function() {
                formItemSelector.getForm().submit(
                {
                    method: 'POST',
                    waitMsg:'Submitting...',
                    reset : false,
                    success : function() {
                        Ext.Msg.alert("Success!");
                    },
                    failure: function(form, action){Ext.Msg.alert('Error',action.result.text);}
                });
            }
        }

buttonReset = {
            text:"Reset",
            handler: function() {
                var i=formItemSelector.getForm().findField("itemselector");
                i.reset.call(i);
            }
        }

    formItemSelector = new Ext.form.FormPanel({
        labelWidth:40,
        width:550,
        url:"/save",
        items:panelItem,
        buttons:[buttonSave, buttonReset]
    });
    formItemSelector.render("item_selector_div");
}

function testLabelWidth() {
  assertNotNaN("Label Width should be an integer!", formItemSelector.labelWidth);
  assertEquals("Label Width value mismatch!", 40, formItemSelector.labelWidth);
}

function testWidth() {
  assertNotNaN("Width should be an integer!", formItemSelector.width);
  assertEquals("Width value mismatch!", 550, formItemSelector.width);
}

function testURL() {
  assertNaN("URL should be a string!", formItemSelector.url);
  assertEquals("URL value mismatch!", "/save", formItemSelector.url);
}

function testXtype() {
  assertNaN("xtype should be a string!", panelItem.xtype);
  assertEquals("xtype value mismatch!", 'itemselector', panelItem.xtype);
}

function testFieldLabel() {
  assertNaN("fieldLabel should be a string!", panelItem.fieldLabel);
  assertEquals("fieldLabel value mismatch!", 'States', panelItem.fieldLabel);
}

function testDataFields0() {
  assertNaN("dataFields[0] should be a string!", panelItem.dataFields[0]);
  assertEquals("dataFields[0] value mismatch!", 'code', panelItem.dataFields[0]);
}

function testDataFields1() {
  assertNaN("dataFields[1] should be a string!", panelItem.dataFields[1]);
  assertEquals("dataFields[1] value mismatch!", 'desc', panelItem.dataFields[1]);
}

function testMsWidth() {
  assertNotNaN("msWidth should be an integer!", panelItem.msWidth);
  assertEquals("msWidth value mismatch!", 200, panelItem.msWidth);
}

function testMsHeight() {
  assertNotNaN("msHeight should be an integer!", panelItem.msHeight);
  assertEquals("msHeight value mismatch!", 200, panelItem.msHeight);
}

function testValueField() {
  assertNaN("valueField should be a string!", panelItem.valueField);
  assertEquals("valueField value mismatch!", 'code', panelItem.valueField);
}

function testDisplayField() {
  assertNaN("displayField should be a string!", panelItem.displayField);
  assertEquals("displayField value mismatch!", 'desc', panelItem.displayField);
}

function testFromLegend() {
  assertNaN("fromLegend should be a string!", panelItem.fromLegend);
  assertEquals("fromLegend value mismatch!", 'Available', panelItem.fromLegend);
}

function testToLegend() {
  assertNaN("toLegend should be a string!", panelItem.toLegend);
  assertEquals("toLegend value mismatch!", 'Selected', panelItem.toLegend);
}

function testButtonSave() {
  assertNaN("buttonSave.text should be a string!", buttonSave.text);
  assertEquals("buttonSave.text value mismatch!", 'Save', buttonSave.text);
}

function testButtonReset() {
  assertNaN("buttonReset.text should be a string!", buttonReset.text);
  assertEquals("buttonReset.text value mismatch!", 'Reset', buttonReset.text);
}

function testTBar() {
  assertNaN("TBar text should be a string!", panelItem.TBar[0].text);
  assertEquals("TBar text value mismatch!", 'Clear', panelItem.TBar[0].text);
}

function testFromData() {
  assertEquals("fromData value mismatch!", 'MA', panelItem.fromData[20][0]);
}

function testToData() {
  //assertEquals("toData value mismatch!", [], panelItem.toData);
}

